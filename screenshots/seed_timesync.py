#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Seed clocks, time services, bounds, resyncs, an NTP policy and clock alerts
(Phase 23.3) for the Time Sync screenshots.

Runs INSIDE the screenshot VM against the sysmanage ORM, like the other
seeders.  Apply via:  make screenshots-timesync-seed

WHAT IT HAS TO SHOW, AND WHY
----------------------------
  * A fleet that is mostly fine, worst first: two Linux servers within a
    millisecond or two, a FreeBSD build box at 210 ms, a Debian VM a few
    milliseconds off but on the wrong NTP servers.
  * win11-ws-01 at +1.33 s -- over the 1 s warning bound -- because Windows
    Time is STOPPED: the case the Phase 23.3 spike found on a real laptop.
    Its offset history climbs over the week, and its last resync failed with
    Windows' own words.
  * macos-studio-01 two hours behind, measured from a REFUSED message's
    timestamp (method "timestamp"), critical -- and its resync "not
    possible" because that agent runs without administrator rights.
  * rhel-db-01 on the "database" tag's tighter bounds (100 ms / 500 ms).
  * A fleet NTP policy (applied, with auto-resync) that most hosts follow;
    debian-app-01 differs, and applying it failed once.
  * Open clock alerts for the two hosts out of bounds.

TIMES: measurements are dated 20 minutes AHEAD.  The demo hosts never
heartbeat, and a clock not measured for 30 minutes is shown as "no recent
measurement" -- a long capture would otherwise cross that line mid-run (the
same trap as screenshot-demo-hosts-go-inactive).

STABLE DURING CAPTURE: the demo hosts are not privileged, and both the NTP
policy tick and auto-resync leave unprivileged hosts alone -- so the enforced
policy shown here never starts pushing plans or queueing resyncs mid-capture.

Run AFTER screenshots-seed (demo hosts).  Idempotent: clears its own rows
first.
"""

import json
import math
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from backend.persistence import db
from backend.persistence.models import (
    Alert,
    AlertRule,
    ClockBound,
    ClockResync,
    Host,
    HostClockSample,
    HostTag,
    NtpPolicy,
    NtpPolicyState,
    Tag,
)

AUTHOR = "admin@sysmanage.org"
DOMAIN = "corp.northstar.io"
POLICY_SERVERS = ["ntp1.corp.northstar.io", "ntp2.corp.northstar.io"]
NOW = datetime.now(timezone.utc).replace(tzinfo=None)
MEASURED = NOW + timedelta(minutes=20)

# name -> (offset ms, rtt ms, method, service, unit, running, synced, enabled,
#          source, stratum, service's own offset, configured servers)
CLOCKS = {
    "ubuntu-web-01": (0.4, 18.2, "exchange", "chrony", "chrony", True, True, True,
                      "10.20.0.11", 2, 0.3, POLICY_SERVERS),
    "rhel-db-01": (-3.2, 21.7, "exchange", "chrony", "chronyd", True, True, True,
                   "10.20.0.12", 2, -3.0, POLICY_SERVERS),
    "debian-app-01": (6.8, 24.9, "exchange", "timesyncd", "systemd-timesyncd", True,
                      True, True, "ntp.ubuntu.com", None, None, ["ntp.ubuntu.com"]),
    "freebsd-build-01": (210.0, 31.4, "exchange", "ntpd", "ntpd", True, True, True,
                         "10.20.0.11", 3, 198.5, POLICY_SERVERS),
    "win11-ws-01": (1330.0, 27.3, "exchange", "w32time", "w32time", False, False, False,
                    None, None, None, ["time.windows.com"]),
    "macos-studio-01": (-7_200_000.0, None, "timestamp", "timed", "timed", None, None,
                        None, None, None, None, None),
}
# How each host's offset moved over the week (ms at "days ago" -> now).
HISTORY = {
    "ubuntu-web-01": lambda f: 0.4 + 0.8 * math.sin(f * 40),
    "rhel-db-01": lambda f: -3.0 + 1.1 * math.sin(f * 33),
    "freebsd-build-01": lambda f: 180 + 30 * f + 6 * math.sin(f * 25),
    "win11-ws-01": lambda f: 40 + 1290 * f ** 1.4,
}


def _host(session, name):
    return session.query(Host).filter(Host.fqdn == f"{name}.{DOMAIN}").first()


def _clear(session):
    for model in (HostClockSample, ClockBound, ClockResync, NtpPolicy, NtpPolicyState):
        session.query(model).delete()
    rules = session.query(AlertRule).filter(AlertRule.condition_type == "clock_offset")
    for rule in rules:
        session.query(Alert).filter(Alert.rule_id == rule.id).delete()
        session.delete(rule)
    session.flush()


def _clock(host, values):
    (offset, rtt, method, service, unit, running, synced, enabled,
     source, stratum, own, servers) = values  # fmt: skip
    host.clock_offset_ms, host.clock_rtt_ms = offset, rtt
    host.clock_samples = 9 if method == "exchange" else 3
    host.clock_method, host.clock_measured_at = method, MEASURED
    host.time_service, host.time_service_unit = service, unit
    host.time_service_running, host.time_synchronized = running, synced
    host.time_service_enabled, host.time_source = enabled, source
    host.time_stratum, host.time_reported_offset_ms = stratum, own
    host.time_configured_servers = None if servers is None else json.dumps(servers)
    host.time_config_path = {
        "chrony": "/etc/chrony/chrony.conf" if unit == "chrony" else "/etc/chrony.conf",
        "ntpd": "/etc/ntp.conf",
        "timesyncd": "/etc/systemd/timesyncd.conf.d",
    }.get(service)
    host.time_status_at = MEASURED


def _history(session, host, curve):
    points = 7 * 24 * 4  # one every 15 minutes, for a week
    for i in range(points):
        fraction = i / (points - 1)
        session.add(
            HostClockSample(
                id=uuid.uuid4(),
                host_id=host.id,
                measured_at=NOW - timedelta(days=7) + timedelta(minutes=15 * i),
                offset_ms=round(curve(fraction), 3),
                rtt_ms=20.0,
                method="exchange",
            )
        )


def _tag_bounds(session, host):
    tag = session.query(Tag).filter(Tag.name == "database").first()
    if tag is None:
        return
    session.add(ClockBound(id=uuid.uuid4(), scope_kind="tag", scope_ref=str(tag.id),
                           warning_ms=100.0, critical_ms=500.0, updated_at=NOW,
                           updated_by=AUTHOR))
    if not session.query(HostTag).filter_by(host_id=host.id, tag_id=tag.id).first():
        session.add(HostTag(id=uuid.uuid4(), host_id=host.id, tag_id=tag.id, created_at=NOW))


def _resync(session, host, status, error=None, detail=None, method=None, hours_ago=2):
    at = NOW - timedelta(hours=hours_ago)
    session.add(
        ClockResync(id=uuid.uuid4(), host_id=host.id, status=status, requested_by=AUTHOR,
                    requested_at=at, sent_at=at, finished_at=at + timedelta(seconds=8),
                    command_id=str(uuid.uuid4()), offset_before_ms=host.clock_offset_ms,
                    service=host.time_service, method=method, error=error, detail=detail)
    )


def _policy(session, debian):
    session.add(NtpPolicy(id=uuid.uuid4(), scope_kind="fleet", scope_ref="",
                          servers=json.dumps(POLICY_SERVERS), enforce=True,
                          auto_resync=True, updated_at=NOW, updated_by=AUTHOR))
    if debian is not None:
        session.add(NtpPolicyState(
            host_id=debian.id, policy_digest="seed", status="failed",
            command_id=str(uuid.uuid4()), attempts=1,
            sent_at=NOW - timedelta(minutes=50), finished_at=NOW - timedelta(minutes=49),
            last_error="systemctl restart systemd-timesyncd: Job for "
                       "systemd-timesyncd.service failed because the control process "
                       "exited with error code.",
        ))


def _alerts(session, out_of_bounds):
    rule = AlertRule(id=uuid.uuid4(), name="Clock offset", condition_type="clock_offset",
                     condition_params={"min_level": "warning", "clear_ratio": 0.8,
                                       "site_digest": {"min_hosts": 5, "min_fraction": 0.5}},
                     severity="high", enabled=True, cooldown_minutes=60,
                     created_at=NOW, updated_at=NOW)
    session.add(rule)
    session.flush()
    for host, severity, message in out_of_bounds:
        session.add(Alert(id=uuid.uuid4(), rule_id=rule.id, host_id=host.id,
                          severity=severity, title=f"Clock offset: {host.fqdn}",
                          message=message, details={"offset_ms": host.clock_offset_ms},
                          triggered_at=NOW - timedelta(minutes=35), notification_sent=True))


def main() -> None:
    session = sessionmaker(bind=db.get_engine())()
    try:
        _clear(session)
        hosts = {}
        for name, values in CLOCKS.items():
            host = _host(session, name)
            if host is None:
                print(f"  - skip {name}: demo host not found (run screenshots-seed first)")
                continue
            _clock(host, values)
            hosts[name] = host
        if not hosts:
            print("  no demo hosts present -- run make screenshots-seed first")
            return
        for name, curve in HISTORY.items():
            if name in hosts:
                _history(session, hosts[name], curve)
        if "rhel-db-01" in hosts:
            _tag_bounds(session, hosts["rhel-db-01"])
        if "win11-ws-01" in hosts:
            _resync(session, hosts["win11-ws-01"], "failed", "command_failed",
                    "The computer did not resync because no time data was available.",
                    "w32tm /resync")
        if "macos-studio-01" in hosts:
            _resync(session, hosts["macos-studio-01"], "unsupported", "not_privileged")
        if "freebsd-build-01" in hosts:
            _resync(session, hosts["freebsd-build-01"], "succeeded", method="ntpdate -b",
                    hours_ago=30)
        _policy(session, hosts.get("debian-app-01"))
        out = []
        if "win11-ws-01" in hosts:
            out.append((hosts["win11-ws-01"], "high",
                        "The clock is 1330 ms off the server, beyond its warning bound "
                        "of 1000 ms."))
        if "macos-studio-01" in hosts:
            out.append((hosts["macos-studio-01"], "critical",
                        "The clock is -7200000 ms off the server, beyond its critical "
                        "bound of 5000 ms."))
        _alerts(session, out)
        session.commit()
        print(f"  + clocks for {len(hosts)} hosts, a week of history, tag bounds, "
              "resyncs, a fleet NTP policy and clock alerts")
    finally:
        session.close()


if __name__ == "__main__":
    main()
