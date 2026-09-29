#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Seed Network Discovery demo data (Phase 21.6 S6) -- through the REAL path.

Runs INSIDE the screenshot VM against the sysmanage ORM, like the other
seeders.  Apply via:  make screenshots-discovery-seed

WHY IT SENDS REPORTS INSTEAD OF WRITING DEVICE ROWS
---------------------------------------------------
Every device on the Network Discovery page is a VERDICT: which device it is,
whether a managed host already covers it, what its MAC says about the vendor,
what the device looks like.  Hand-written rows would document what we meant
the engine to decide.  This seeder writes what AGENTS would send -- neighbor
reports from three demo hosts -- and hands them to the same service the
WebSocket handler calls, with the licensed asset_discovery_engine, so every
vendor, "looks like" guess, managed match and blind spot on screen is one the
product computed.  Exclusions go through the real review functions, and the
sweep is requested and answered through the real sweep path.

WHAT IT HAS TO SHOW, AND WHY
----------------------------
  * Managed hosts suppressed: each observer sees its neighbors' MACs, and
    they land on the Managed tab, not the review queue.
  * Evidence: a printer that announces itself over mDNS, a streaming box over
    SSDP, a NAS -- and a silent Raspberry Pi only the sweep found.
  * The honest edges: a phone with a locally administered MAC ("address may
    change") and a device heard only by IP ("no MAC seen").
  * Blind spots: win11-ws-01 reports with ARP listening unavailable (Windows),
    so the page states what that observer cannot see.
  * Exclusions with reasons: a switch marked as network equipment by MAC, and
    a static virtual-router address registered by IP.

Run AFTER screenshots-seed (demo hosts + their interfaces).  Idempotent: clears
network discovery's own rows first.
"""

import asyncio
import json

from sqlalchemy.orm import sessionmaker

from backend.persistence import db
from backend.persistence.models import Host, User
from backend.persistence.models.asset_discovery import (
    DiscoveredAsset,
    DiscoveredAssetExclusion,
    DiscoveredAssetSighting,
    NetworkDiscoveryDispatch,
    NetworkDiscoveryObserver,
    NetworkDiscoveryPolicy,
    NetworkSweepRun,
)

ENGINE = "asset_discovery_engine"
LAN = "10.20.0"
WEB = "ubuntu-web-01.corp.northstar.io"
DB_HOST = "rhel-db-01.corp.northstar.io"
WIN = "win11-ws-01.corp.northstar.io"
REPORT_INTERVAL = 3600
DISCOVERY_COMMANDS = ("configure_network_discovery", "run_network_sweep")

# Real IEEE prefixes, so the shipped OUI table resolves each vendor.
PRINTER = ("3c:52:82:4e:19:a0", "10.20.0.120")  # Hewlett Packard
NAS = ("00:11:32:8a:02:5c", "10.20.0.130")  # Synology
STREAMER = ("b0:a7:37:61:c4:02", "10.20.0.141")  # Roku
SWITCH = ("00:1b:54:3a:10:01", "10.20.0.2")  # Cisco
PI = ("dc:a6:32:07:5b:e1", "10.20.0.150")  # Raspberry Pi -- silent
PHONE = ("da:1f:3c:92:7e:44", "10.20.0.162")  # locally administered
ROUTER_VIP = ("00:00:5e:00:01:0a", "10.20.0.1")  # VRRP virtual router

OK = "ok"
LINUX_METHODS = {
    "arp_listen": OK, "nd_listen": OK, "mdns": OK, "ssdp": OK, "cache": OK,
    "sweep": "unavailable:disabled",
}  # fmt: skip
WINDOWS_METHODS = {
    "arp_listen": "unavailable:unsupported_platform",
    "nd_listen": "unavailable:unsupported_platform",
    "mdns": OK, "ssdp": OK, "cache": OK, "sweep": "unavailable:disabled",
}  # fmt: skip


def _obs(mac, ip, methods, count=1, hostnames=(), mdns=(), ssdp=(), iface="eth0"):
    return {
        "mac": mac,
        "ips": [ip],
        "interface": iface,
        "methods": list(methods),
        "count": count,
        "hostnames": list(hostnames),
        "evidence": {"mdns_services": list(mdns), "ssdp": list(ssdp)},
    }


def _interfaces(host, name="eth0"):
    return [{"name": name, "mac": host.interface_mac, "ip": host.ipv4, "prefix": 24}]


def _mac_of(session, host):
    from backend.persistence.models import NetworkInterface  # noqa: PLC0415

    row = (
        session.query(NetworkInterface.mac_address)
        .filter(NetworkInterface.host_id == host.id, NetworkInterface.mac_address.isnot(None))
        .first()
    )
    return row.mac_address.lower() if row else None


def _reports(hosts):
    web, dbh, win = hosts[WEB], hosts[DB_HOST], hosts[WIN]
    neighbors = [
        _obs(dbh.interface_mac, dbh.ipv4, ["arp_listen", "cache"], 41),
        _obs(win.interface_mac, win.ipv4, ["arp_listen"], 7),
    ]
    web_report = {
        "interfaces": _interfaces(web),
        "methods": LINUX_METHODS,
        "window_seconds": REPORT_INTERVAL,
        "observations": neighbors + [
            _obs(*PRINTER, ["arp_listen", "mdns"], 12, ["NPI4E19A0.local"],
                 mdns=["_ipp._tcp", "_printer._tcp", "_pdl-datastream._tcp"]),
            _obs(*NAS, ["arp_listen", "mdns"], 9, ["backup-nas.local"],
                 mdns=["_smb._tcp", "_afpovertcp._tcp", "_http._tcp"]),
            _obs(*STREAMER, ["arp_listen", "ssdp"], 5,
                 ssdp=["ST: roku:ecp", "SERVER: Roku/12.5.0 UPnP/1.0"]),
            _obs(*SWITCH, ["arp_listen", "cache"], 22),
            _obs(*PHONE, ["arp_listen", "mdns"], 3, mdns=["_companion-link._tcp"]),
            _obs(*ROUTER_VIP, ["arp_listen", "cache"], 64),
        ],
    }  # fmt: skip
    db_report = {
        "interfaces": _interfaces(dbh),
        "methods": LINUX_METHODS,
        "window_seconds": REPORT_INTERVAL,
        "observations": [
            _obs(web.interface_mac, web.ipv4, ["arp_listen", "cache"], 57),
            _obs(*PRINTER, ["arp_listen"], 4),
            _obs(*ROUTER_VIP, ["arp_listen", "cache"], 60),
        ],
    }
    # Windows: no raw capture, so mDNS/SSDP by IP -- one device never resolves
    # to a MAC and is shown as "No MAC seen".
    win_report = {
        "interfaces": _interfaces(win, "Ethernet"),
        "methods": WINDOWS_METHODS,
        "window_seconds": REPORT_INTERVAL,
        "observations": [
            _obs(*STREAMER, ["ssdp"], 2, iface="Ethernet",
                 ssdp=["ST: roku:ecp", "SERVER: Roku/12.5.0 UPnP/1.0"]),
            _obs(None, LAN + ".177", ["mdns"], 2, iface="Ethernet",
                 mdns=["_googlecast._tcp"]),
        ],
    }  # fmt: skip
    return [(web, web_report), (dbh, db_report), (win, win_report)]


def _clear(session):
    for model in (
        DiscoveredAssetSighting,
        DiscoveredAssetExclusion,
        DiscoveredAsset,
        NetworkSweepRun,
        NetworkDiscoveryObserver,
        NetworkDiscoveryDispatch,
        NetworkDiscoveryPolicy,
    ):
        session.query(model).delete()


def _advertise(host):
    """Add the discovery commands to the host's EXISTING capability report, so
    the reconcile tick and the sweep picker treat it as equipped."""
    report = json.loads(host.agent_capabilities) if host.agent_capabilities else None
    if not isinstance(report, dict) or not isinstance(report.get("commands"), list):
        print(f"  note: {host.fqdn} has no capability report; it will not sweep")
        return
    for command in DISCOVERY_COMMANDS:
        if command not in report["commands"]:
            report["commands"].append(command)
    host.agent_capabilities = json.dumps(report)


async def _boot_engine():
    from backend.licensing.license_service import license_service  # noqa: PLC0415
    from backend.licensing.module_loader import module_loader  # noqa: PLC0415

    await license_service.initialize()
    module_loader.initialize()
    if not await module_loader.ensure_module_available(ENGINE):
        raise SystemExit(f"{ENGINE} is not available -- is this the Enterprise VM?")


def _admin(session):
    admin = session.query(User).filter(User.is_admin.is_(True)).first()
    if admin is None:
        raise SystemExit("no administrator in the demo database -- run screenshots-seed first")
    return admin.userid


def _sweep(session, hosts, actor):
    """One sweep, requested and answered through the real path: the Pi that
    never spoke is found here and nowhere else."""
    from backend.services import asset_discovery_service as svc  # noqa: PLC0415
    from backend.services import network_sweep  # noqa: PLC0415

    try:
        run = network_sweep.request_sweep(session, LAN + ".0/24", 50, actor)
    except network_sweep.SweepError as error:
        print(f"  note: sweep not requested ({error}); the Sweeps tab stays empty")
        return
    sweeper = next(h for h in hosts.values() if str(h.id) == run["agent_host_id"])
    found = [
        _obs(*PI, ["sweep"]),
        _obs(*PRINTER, ["sweep"]),
        _obs(*NAS, ["sweep"]),
        _obs(*SWITCH, ["sweep"]),
    ]
    # The sweeper's OWN capabilities: the engine picks any equipped agent,
    # and a Windows sweeper must not suddenly claim ARP listening.
    own = WINDOWS_METHODS if sweeper.fqdn == WIN else LINUX_METHODS
    methods = dict(own, sweep=OK)
    svc.record_report(
        session,
        sweeper.id,
        {
            "interfaces": _interfaces(sweeper),
            "methods": methods,
            "window_seconds": None,
            "observations": found,
            "sweep": {"run_id": run["id"], "cidr": run["cidr"], "status": "completed",
                      "probed": 254, "reason": None},
        },
    )  # fmt: skip
    print(f"  sweep of {run['cidr']} by {sweeper.fqdn}: {len(found)} devices answered")


def _exclude(session, actor):
    from backend.services import asset_discovery_review as review  # noqa: PLC0415

    switch = session.query(DiscoveredAsset).filter(DiscoveredAsset.identity == SWITCH[0]).first()
    if switch is not None:
        review.exclude(
            session, [switch.id], "network_equipment",
            "Core access switch in the server-room rack, managed by the network team", actor,
        )  # fmt: skip
    review.exclude_address(
        session, ROUTER_VIP[1], "virtual_address",
        "VRRP gateway address shared by the two edge routers", actor,
    )  # fmt: skip


def main():
    session = sessionmaker(bind=db.get_engine())()
    try:
        hosts = {h.fqdn: h for h in session.query(Host).all()}
        missing = [f for f in (WEB, DB_HOST, WIN) if f not in hosts]
        if missing:
            raise SystemExit(f"demo hosts missing ({missing}) -- run screenshots-seed first")
        for fqdn in (WEB, DB_HOST, WIN):
            hosts[fqdn].interface_mac = _mac_of(session, hosts[fqdn])
            _advertise(hosts[fqdn])
        _clear(session)
        session.commit()
    except BaseException:
        session.close()
        raise

    asyncio.run(_boot_engine())
    from backend.services import asset_discovery_service as svc  # noqa: PLC0415
    from backend.services import network_discovery_policy as policy  # noqa: PLC0415

    try:
        actor = _admin(session)
        # Hourly reports: an observer counts as stale after 3 missed intervals,
        # and the demo hosts never report again, so at 5 minutes every agent
        # read "has stopped reporting" by the time the Enterprise capture got
        # to these shots (15 minutes).  An hour gives the whole run 3 hours.
        policy.set_policy(
            session, True, REPORT_INTERVAL, actor, sweep_enabled=True, retention_days=30
        )
        for host, report in _reports(hosts):
            outcome = svc.record_report(session, host.id, report)
            print(f"  report from {host.fqdn}: {outcome}")
        session.commit()
        _sweep(session, hosts, actor)
        session.commit()
        _exclude(session, actor)
        session.commit()
        from backend.services import asset_discovery_review as review  # noqa: PLC0415

        counts = review.summary(session)["counts"]
        print(f"network discovery: {counts}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
