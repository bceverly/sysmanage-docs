#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Seed hardware health (Phase 23.1) for the Hardware Health screenshots --
by feeding agent-shaped reports through the REAL ingestion code.

Runs INSIDE the screenshot VM against the sysmanage ORM, like the other
seeders.  Apply via:  make screenshots-hardware-seed

WHY IT SENDS REPORTS INSTEAD OF WRITING ROWS
--------------------------------------------
Each report below has the exact shape the agent sends (``collection/
hardware_health.py``: components with kind / id / name / state / reason
codes / metrics / source, plus the sources that ran, were absent or
failed).  ``services.hardware_health.apply_report`` stores them, so every
event, state change and host status in the screenshots is one the product
computed -- including the operating system's own evidence, which becomes a
"system" event exactly as a triggered report does.

WHAT IT HAS TO SHOW, AND WHY
----------------------------
  * rhel-db-01 losing a disk: sdb fails its SMART check, the md RAID1 array
    md0 runs degraded on one disk, and the kernel's own lines (the md
    "Disk failure" message) arrive as evidence.  It was healthy three days
    ago, so the events read as changes, not as a host born broken.
  * freebsd-build-01's NVMe with 19 media errors (the real lab drive the
    23.1 spike found) -- a warning, already acknowledged with a note -- on
    a healthy ZFS pool, GEOM classes not loaded.
  * debian-app-01's SATA drive NOT JUDGED because smartctl is absent, so the
    smartmontools recommendation shows on the host and on the fleet page.
  * ubuntu-web-01 all healthy, with hwmon temperature sensors (folded away
    on the host card) and EDAC memory counts.  It runs hot by design and has
    its own temperature warning limit of 95 C: its cores read 86-89 C, above
    the 82 C the hardware declares, and are healthy under the host's limit
    (the hardware-health-templimit shot).
  * win11-ws-01 healthy through the Windows storage cmdlets.
  * macos-studio-01 never reported -- "Not reported", never "Healthy".
  * Open hardware alerts: critical for rhel-db-01, high for freebsd-build-01
    (shown where the alerting engine is licensed).

TIMES: the current reports are dated 20 minutes AHEAD.  The demo hosts never
heartbeat, and a host whose last report is more than an hour old is shown as
"No recent report" -- a long capture would otherwise cross that line mid-run
(the same trap as screenshot-demo-hosts-go-inactive).  The demo hosts are
also woken (active, last access now), because the smartmontools
recommendation lists only active hosts.

Run AFTER screenshots-seed (demo hosts).  Idempotent: clears its own rows
first.
"""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from backend.persistence import db
from backend.persistence.models import (
    Alert,
    AlertRule,
    HardwareComponent,
    HardwareEvent,
    HardwareToolInstall,
    Host,
)
from backend.services import hardware_health

AUTHOR = "admin@sysmanage.org"
DOMAIN = "corp.northstar.io"
NOW = datetime.now(timezone.utc).replace(tzinfo=None)
CURRENT = NOW + timedelta(minutes=20)


def _src(name, status="ran", detail=None):
    out = {"name": name, "status": status}
    if detail:
        out["detail"] = detail
    return out


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def _comp(kind, ident, name, state, source, reasons=None, metrics=None):
    return {"kind": kind, "id": ident, "name": name, "state": state,
            "reasons": reasons or [], "metrics": metrics or {}, "source": source}  # fmt: skip


def _hwmon(chip, sensors):
    """hwmon temperatures as the Linux collector reports them."""
    return [
        _comp("sensor", f"{chip}/{sensor}", f"{chip} {label}", "ok", "hwmon",
              metrics={"temperature_c": value, "high_c": high, "critical_c": crit})
        for sensor, label, value, high, crit in sensors
    ]  # fmt: skip


CORETEMP = [
    ("temp1", "Package id 0", 47.0, 82.0, 100.0),
    ("temp2", "Core 0", 44.0, 82.0, 100.0),
    ("temp3", "Core 1", 46.0, 82.0, 100.0),
    ("temp4", "Core 2", 43.0, 82.0, 100.0),
    ("temp5", "Core 3", 45.0, 82.0, 100.0),
]

# ubuntu-web-01: a hot-by-design host (a laptop serving with its lid closed)
# with its own warning limit -- above the 82 C its hardware declares.
HOT_LIMIT_C = 95.0
CORETEMP_HOT = [
    ("temp1", "Package id 0", 89.0, 82.0, 100.0),
    ("temp2", "Core 0", 87.0, 82.0, 100.0),
    ("temp3", "Core 1", 88.0, 82.0, 100.0),
    ("temp4", "Core 2", 86.0, 82.0, 100.0),
    ("temp5", "Core 3", 87.0, 82.0, 100.0),
]


def _hot_coretemp():
    """As the agent reports them: WARNING against the 82 C the hardware
    declares.  The server re-judges them against the host's own limit."""
    return [
        _comp("sensor", f"coretemp/{sensor}", f"coretemp {label}", "warning", "hwmon",
              reasons=[{"code": "temperature_high", "value": value, "limit": high}],
              metrics={"temperature_c": value, "high_c": high, "critical_c": crit})
        for sensor, label, value, high, crit in CORETEMP_HOT
    ]  # fmt: skip


def _ubuntu():
    nvme = {"critical_warning": 0, "temperature_c": 39.0, "available_spare": 100,
            "available_spare_threshold": 10, "percent_used": 2, "power_on_hours": 8760,
            "unsafe_shutdowns": 4, "media_errors": 0, "error_log_entries": 0}  # fmt: skip
    return {
        "components": [
            _comp("drive", "nvme0", "SAMSUNG MZQL21T9HCJR-00A07", "ok", "nvme",
                  metrics=nvme),
            *_hot_coretemp(),
            *_hwmon("nvme", [("temp1", "Composite", 39.0, 84.8, 84.8)]),
            _comp("memory", "mc0", "memory controller mc0", "ok", "edac",
                  metrics={"corrected_errors": 0, "uncorrected_errors": 0}),
        ],
        "sources": [_src("nvme"), _src("mdstat", "absent"), _src("zpool", "absent"),
                    _src("hwmon"), _src("edac")],
    }  # fmt: skip


def _rhel(failing):
    """Healthy three days ago; now sdb has failed and md0 runs on sda."""
    smart = {"temperature_c": 36, "reallocated_sectors": 0, "pending_sectors": 0,
             "offline_uncorrectable": 0}  # fmt: skip
    sdb, md0 = (
        _comp("drive", "sdb", "ST4000NM000A-2HZ100", "ok", "smartctl", metrics=smart),
        _comp("array", "md0", "md0", "ok", "mdstat",
              metrics={"level": "raid1", "raid_devices": 2, "active_devices": 2}),
    )  # fmt: skip
    if failing:
        sdb = _comp(
            "drive", "sdb", "ST4000NM000A-2HZ100", "failed", "smartctl",
            reasons=[{"code": "smart_failed"},
                     {"code": "reallocated_sectors", "count": 1288},
                     {"code": "pending_sectors", "count": 96}],
            metrics={**smart, "temperature_c": 41, "reallocated_sectors": 1288,
                     "pending_sectors": 96},
        )  # fmt: skip
        md0 = _comp(
            "array", "md0", "md0", "warning", "mdstat",
            reasons=[{"code": "array_degraded", "active": 1, "total": 2},
                     {"code": "failed_members", "members": ["sdb1"]}],
            metrics={"level": "raid1", "raid_devices": 2, "active_devices": 1},
        )  # fmt: skip
    return {
        "components": [
            _comp("drive", "sda", "ST4000NM000A-2HZ100", "ok", "smartctl", metrics=smart),
            sdb,
            md0,
            *_hwmon("coretemp", CORETEMP[:3]),
            _comp("memory", "mc0", "memory controller mc0", "ok", "edac",
                  metrics={"corrected_errors": 0, "uncorrected_errors": 0}),
        ],
        "sources": [_src("nvme", "absent"), _src("smartctl"), _src("mdstat"),
                    _src("zpool", "absent"), _src("hwmon"), _src("edac")],
    }  # fmt: skip


IO_ERROR = "I/O error, dev sdb, sector 1953520 op 0x0:(READ) flags 0x0 phys_seg 1 prio class 2"
RHEL_EVIDENCE = [
    {"category": "storage", "source": "kernel", "text": IO_ERROR},
    {"category": "storage", "source": "kernel",
     "text": "md/raid1:md0: Disk failure on sdb1, disabling device."},
    {"category": "storage", "source": "kernel",
     "text": "md/raid1:md0: Operation continuing on 1 devices."},
]  # fmt: skip


def _debian():
    return {
        "components": [
            _comp("drive", "sda", "ST2000NM000A-2J2100", "unknown", None,
                  reasons=[{"code": "smartctl_absent"}]),
            *_hwmon("acpitz", [("temp1", "temp1", 27.8, None, 105.0)]),
        ],
        "sources": [_src("nvme", "absent"), _src("smartctl", "absent"),
                    _src("mdstat", "absent"), _src("zpool", "absent"), _src("hwmon"),
                    _src("edac", "absent")],
    }  # fmt: skip


def _freebsd(media_errors):
    nvme = {"critical_warning": 0, "temperature_c": 38.0, "available_spare": 100,
            "available_spare_threshold": 10, "percent_used": 7, "power_on_hours": 21843,
            "unsafe_shutdowns": 61, "media_errors": media_errors,
            "error_log_entries": 2214}  # fmt: skip
    state, reasons = "ok", []
    if media_errors:
        state, reasons = "warning", [{"code": "media_errors", "count": media_errors}]
    return {
        "components": [
            _comp("drive", "nvme0", "CT1000P1SSD8", state, "nvmecontrol", reasons, nvme),
            _comp("pool", "zroot", "zroot", "ok", "zpool",
                  metrics={"read": 0, "write": 0, "cksum": 0, "health": "ONLINE",
                           "scan": "scrub repaired 0B in 00:04:12 with 0 errors"}),
            *[_comp("sensor", f"cpu{n}", f"CPU {n}", "ok", "sysctl",
                    metrics={"temperature_c": 41.0 + n}) for n in range(4)],
        ],
        "sources": [_src("nvmecontrol"), _src("zpool"),
                    _src("gmirror", "absent", "class not loaded"),
                    _src("graid", "absent", "class not loaded"),
                    _src("sysctl temperatures")],
    }  # fmt: skip


def _windows():
    disk = {"temperature_c": 41, "percent_used": 3, "read_errors": 0, "write_errors": 0,
            "power_on_hours": 4120, "bus": "NVMe", "media": "SSD"}  # fmt: skip
    return {
        "components": [
            _comp("drive", "disk0", "Samsung SSD 990 PRO 2TB", "ok", "Get-PhysicalDisk",
                  metrics=disk),
            _comp("sensor", "acpi/ThermalZone\\TZ00_0", "ACPI ThermalZone\\TZ00_0", "ok",
                  "MSAcpi_ThermalZoneTemperature",
                  metrics={"temperature_c": 28.0, "critical_c": 105.0}),
        ],
        "sources": [_src("powershell storage")],
    }  # fmt: skip


def _host(session, name):
    return session.query(Host).filter(Host.fqdn == f"{name}.{DOMAIN}").first()


def _clear(session):
    for model in (HardwareEvent, HardwareComponent, HardwareToolInstall):
        session.query(model).delete()
    session.query(Host).update(
        {Host.hardware_state: None, Host.hardware_reported_at: None,
         Host.hardware_sources: None, Host.hardware_temp_warning_c: None},
        synchronize_session=False,
    )  # fmt: skip
    rules = session.query(AlertRule).filter(AlertRule.condition_type == "hardware_health")
    for rule in rules:
        session.query(Alert).filter(Alert.rule_id == rule.id).delete()
        session.delete(rule)
    session.flush()


def _wake(hosts):
    """Active, as anything gated on Host.active (the smartmontools list) needs."""
    for host in hosts.values():
        if host.approval_status == "approved":
            host.status, host.active, host.last_access = "up", True, NOW


def _report(session, host, payload, at, evidence=None):
    if evidence:
        payload = {**payload, "evidence": evidence}
    events = hardware_health.apply_report(session, host, payload, now=at)
    session.flush()
    return events


def _seed_reports(session, hosts):
    if "ubuntu-web-01" in hosts:
        # The limit is set BEFORE the report: it is applied when a report
        # arrives, exactly as on a live server.
        hosts["ubuntu-web-01"].hardware_temp_warning_c = HOT_LIMIT_C
        _report(session, hosts["ubuntu-web-01"], _ubuntu(), CURRENT)
    if "rhel-db-01" in hosts:
        rhel = hosts["rhel-db-01"]
        _report(session, rhel, _rhel(False), NOW - timedelta(days=3))
        _report(session, rhel, _rhel(True), NOW - timedelta(minutes=42), RHEL_EVIDENCE)
        _report(session, rhel, _rhel(True), CURRENT)  # unchanged: no new events
    if "debian-app-01" in hosts:
        _report(session, hosts["debian-app-01"], _debian(), CURRENT)
    if "freebsd-build-01" in hosts:
        bsd = hosts["freebsd-build-01"]
        _report(session, bsd, _freebsd(0), NOW - timedelta(days=12))
        for event in _report(session, bsd, _freebsd(19), NOW - timedelta(days=2)):
            hardware_health.acknowledge(
                session, str(event.id), AUTHOR,
                "Replacement drive ordered; this disk only holds the build cache.",
            )  # fmt: skip
        _report(session, bsd, _freebsd(19), CURRENT)
    if "win11-ws-01" in hosts:
        _report(session, hosts["win11-ws-01"], _windows(), CURRENT)
    # macos-studio-01 is left alone on purpose: never reported.


def _alerts(session, hosts):
    params = {"min_level": "warning", "renotify_minutes": 240, "respect_maintenance": True,
              "site_digest": {"min_hosts": 5, "min_fraction": 0.5}}  # fmt: skip
    rule = AlertRule(id=uuid.uuid4(), name="Hardware health", condition_type="hardware_health",
                     condition_params=params, severity="high", enabled=True,
                     cooldown_minutes=60, created_at=NOW, updated_at=NOW)  # fmt: skip
    session.add(rule)
    session.flush()
    open_alerts = (
        ("rhel-db-01", "critical", "Hardware has failed: ST4000NM000A-2HZ100.", 41),
        ("freebsd-build-01", "high", "Hardware needs attention: CT1000P1SSD8.", 60 * 48),
    )
    for name, severity, message, minutes_ago in open_alerts:
        host = hosts.get(name)
        if host is None:
            continue
        problems = hardware_health.problems_by_host(session, [host.id], per_host=50)
        components = [
            {k: c.get(k) for k in ("kind", "id", "name", "state", "reasons")}
            for c in problems.get(str(host.id), [])[:10]
        ]
        session.add(Alert(
            id=uuid.uuid4(), rule_id=rule.id, host_id=host.id, severity=severity,
            title=f"{rule.name}: {host.fqdn}", message=message,
            details={"status": hardware_health.host_status(host), "site_id": None,
                     "components": components,
                     "level": "critical" if severity == "critical" else "warning"},
            triggered_at=NOW - timedelta(minutes=minutes_ago), notification_sent=True,
        ))  # fmt: skip


def main() -> None:
    session = sessionmaker(bind=db.get_engine())()
    try:
        _clear(session)
        names = ("ubuntu-web-01", "rhel-db-01", "debian-app-01", "freebsd-build-01",
                 "win11-ws-01", "macos-studio-01")  # fmt: skip
        hosts = {}
        for name in names:
            host = _host(session, name)
            if host is None:
                print(f"  - skip {name}: demo host not found (run screenshots-seed first)")
                continue
            hosts[name] = host
        if not hosts:
            print("  no demo hosts present -- run make screenshots-seed first")
            return
        _wake(hosts)
        _seed_reports(session, hosts)
        _alerts(session, hosts)
        session.commit()
        reported = sum(1 for h in hosts.values() if h.hardware_reported_at is not None)
        events = session.query(HardwareEvent).count()
        print(f"  + hardware reports for {reported} hosts through the real ingestion "
              f"({events} events), the smartmontools case and hardware alerts")
    finally:
        session.close()


if __name__ == "__main__":
    main()
