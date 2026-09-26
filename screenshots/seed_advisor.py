#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Seed advisor demo data (Phase 21.2 S8) -- by running the REAL advisor.

Runs INSIDE the screenshot VM against the sysmanage ORM, like the other
seeders.  Apply via:  make screenshots-advisor-seed

WHY IT EVALUATES INSTEAD OF WRITING RESULT ROWS
-----------------------------------------------
Hand-written outcomes would document what we MEANT the advisor to say.  This
seeder gives the demo fleet evidence and runs one real evaluation pass --
the shipped curated pack, the licensed engine, the ordinary tick -- so every
outcome, gap reason, score and proposed fix in the screenshots is one the
product computed.  It also means a tick firing mid-capture recomputes the
SAME answers rather than overwriting fixtures.

WHAT IT HAS TO SHOW, AND WHY
----------------------------
The advisor exists to keep "could not assess" from reading as "clean", so the
fixture must contain hosts it CANNOT assess -- a fleet where everything
answers would document the feature without showing the thing it is for:

  ubuntu-web-01   fresh evidence: pending security updates (-> a proposed
                  fix), a required reboot, CVE findings, a nearly full /var
  rhel-db-01      fresh evidence, nothing pending -- clean where assessed
  debian-app-01   update detection 5 days old -> "too old to trust"
  freebsd / win11 / macos
                  update detection never reported -> "never reported";
                  their fact tables were never collected

Run AFTER screenshots-seed, screenshots-pro-seed and screenshots-ent-seed
(demo hosts, vulnerability and compliance scans).  Idempotent: clears the
advisor's own rows and the evidence it adds, then re-evaluates.
"""
import asyncio
import json
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from backend.persistence import db
from backend.persistence.models import (
    AdvisorProposal,
    AdvisorResult,
    Host,
    PackageUpdate,
    QueryPackResultRow,
    QueryPackRun,
)

NOW = datetime.now(timezone.utc).replace(tzinfo=None)
WEB = "ubuntu-web-01.corp.northstar.io"
DB_HOST = "rhel-db-01.corp.northstar.io"
STALE = "debian-app-01.corp.northstar.io"
ADVISOR_PACK = "advisor-facts"

SECURITY_UPDATES = [
    ("openssl", "3.0.13-0ubuntu3.4", "3.0.13-0ubuntu3.5"),
    ("libssl3t64", "3.0.13-0ubuntu3.4", "3.0.13-0ubuntu3.5"),
    ("curl", "8.5.0-2ubuntu10.4", "8.5.0-2ubuntu10.6"),
    ("libcurl4t64", "8.5.0-2ubuntu10.4", "8.5.0-2ubuntu10.6"),
]

MOUNT_COLUMNS = ["device", "path", "type", "blocks", "blocks_available"]
MOUNTS = [
    {"device": "/dev/sda2", "path": "/", "type": "ext4", "blocks": 25600000, "blocks_available": 13800000},
    {"device": "/dev/sdb1", "path": "/var", "type": "xfs", "blocks": 51200000, "blocks_available": 2900000},
    {"device": "/dev/loop3", "path": "/snap/core22/1380", "type": "squashfs", "blocks": 18000, "blocks_available": 0},
]
USER_COLUMNS = ["uid", "username"]
USERS = [{"uid": "0", "username": "root"}, {"uid": "1000", "username": "deploy"}]


def _clear(session, hosts):
    ids = [h.id for h in hosts.values()]
    session.query(AdvisorProposal).delete(synchronize_session=False)
    session.query(AdvisorResult).delete(synchronize_session=False)
    for run in session.query(QueryPackRun).filter(QueryPackRun.pack_name == ADVISOR_PACK).all():
        session.delete(run)
    session.query(PackageUpdate).filter(
        PackageUpdate.host_id.in_(ids), PackageUpdate.description == "advisor-demo"
    ).delete(synchronize_session=False)
    session.flush()


def _advertise_facts(host):
    """Add contract-v3 fact coverage (with columns) to the host's EXISTING
    capability report.  Only the ``facts`` key is touched: rewriting the
    command list would change how the host reads on every other screen (a
    "limited agent" chip), and those shots are not this seeder's business."""
    report = json.loads(host.agent_capabilities) if host.agent_capabilities else None
    if not isinstance(report, dict) or not report.get("commands"):
        print(f"  note: {host.fqdn} has no capability report; its fact rules stay not assessable")
        return
    report["facts"] = {
        "contract_version": 3,
        "served": {"mounts": "native", "users": "native"},
        "unsupported": {},
        "not_applicable": {},
        "columns": {"mounts": MOUNT_COLUMNS, "users": USER_COLUMNS},
    }
    host.agent_capabilities = json.dumps(report)


def _collected(session, host, table, rows):
    """An ``advisor.<table>`` collection that came back, as the agent sends it."""
    run = QueryPackRun(
        id=uuid.uuid4(), host_id=host.id, pack_name=ADVISOR_PACK, status="success",
        queries_total=1, queries_ok=1, contract_version=3,
        started_at=NOW - timedelta(minutes=20), completed_at=NOW - timedelta(minutes=19),
    )
    session.add(run)
    session.flush()
    for row in rows:
        session.add(QueryPackResultRow(
            id=uuid.uuid4(), run_id=run.id, query_name="advisor." + table,
            status="ok", columns=row, collected_at=NOW - timedelta(minutes=19),
        ))


def _evidence(session, hosts):
    web, dbh, stale = hosts[WEB], hosts[DB_HOST], hosts[STALE]
    for host in (web, dbh):
        host.updates_updated_at = NOW - timedelta(hours=1)
        host.software_updated_at = NOW - timedelta(hours=1)
        host.reboot_required_updated_at = NOW - timedelta(hours=1)
    web.reboot_required = True
    web.reboot_required_reason = "Kernel update installed"
    dbh.reboot_required = False
    stale.updates_updated_at = NOW - timedelta(days=5)
    for name, current, available in SECURITY_UPDATES:
        session.add(PackageUpdate(
            host_id=web.id, package_name=name, current_version=current,
            available_version=available, package_manager="apt", update_type="security",
            status="available", description="advisor-demo", discovered_at=NOW,
            created_at=NOW, updated_at=NOW,
        ))
    _advertise_facts(web)
    _collected(session, web, "mounts", MOUNTS)
    _collected(session, web, "users", USERS)


async def _boot_engines():
    from backend.licensing.license_service import license_service  # noqa: PLC0415
    from backend.licensing.module_loader import module_loader  # noqa: PLC0415

    await license_service.initialize()
    module_loader.initialize()
    if not await module_loader.ensure_module_available("advisor_engine"):
        raise SystemExit("advisor_engine is not available -- is this the Enterprise VM?")


def main():
    session = sessionmaker(bind=db.get_engine())()
    try:
        hosts = {h.fqdn: h for h in session.query(Host).all()}
        missing = [f for f in (WEB, DB_HOST, STALE) if f not in hosts]
        if missing:
            raise SystemExit(f"demo hosts missing ({missing}) -- run screenshots-seed first")
        _clear(session, hosts)
        _evidence(session, hosts)
        session.commit()
    finally:
        session.close()

    asyncio.run(_boot_engines())
    from backend.services import advisor_tick  # noqa: PLC0415

    summary = advisor_tick.run_one_tick()
    print(
        f"advisor: {summary['hosts']} hosts evaluated, {summary['results']} results, "
        f"{summary['proposals_opened']} fix(es) proposed, "
        f"{summary['host_errors']} host errors"
    )


if __name__ == "__main__":
    main()
