#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Seed query-pack + watched-file demo data (Phase 21.1 S4/S5/S7).

Runs INSIDE the screenshot VM against the sysmanage ORM, the same
direct-to-DB approach as seed_pro.py / seed_ent.py / seed_ent_config.py.
Apply via:  make screenshots-facts-seed

WHY ITS OWN SEEDER
------------------
The seeders are piped to the VM over stdin, so a sibling module cannot be
imported on the far side; one seeder per feature area with its own target is
the pattern the repo already uses five times.

WHAT IT HAS TO SHOW, AND WHY
----------------------------
These pages exist to make one distinction visible, so the fixture has to
contain it. Every run below includes hosts that ANSWERED and hosts that COULD
NOT BE ASKED -- a fleet where everything answers would produce screenshots
that document the feature without showing the thing it is for.

Covers:
  query_pack_engine -> query_pack (+ queries, assignments, runs, result rows)
  file watches      -> file_watch (+ paths, assignment) + host_file_state

NOT seeded: query_pack_live_query. LiveQueryPanel holds a SINGLE client-side
state, set only when an operator launches a query in that session, and nothing
lists past ones -- so a seeded row is unreachable from the UI and would only
imply a screen that does not exist.

Run AFTER make screenshots-seed (demo hosts). Idempotent: clears the rows it
manages (FK-safe order) then re-inserts.
"""
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from backend.persistence import db
from backend.persistence.models import (
    FileWatch,
    FileWatchAssignment,
    FileWatchPath,
    Host,
    HostFileState,
    QueryPack,
    QueryPackAssignment,
    QueryPackQuery,
    QueryPackResultRow,
    QueryPackRun,
)

AUTHOR = "admin@sysmanage.org"

DEMO_FQDNS = [
    "ubuntu-web-01.corp.northstar.io",
    "rhel-db-01.corp.northstar.io",
    "debian-app-01.corp.northstar.io",
    "freebsd-build-01.corp.northstar.io",
    "win11-ws-01.corp.northstar.io",
    "macos-studio-01.corp.northstar.io",
]

# Real contract tables and real SQL against them -- the pack list shows the
# query count and the detail view shows the SQL, so filler would read as a
# mock rather than as the product.
PACKS = [
    (
        "ssh-exposure",
        "Which hosts expose SSH beyond the management network.",
        [
            (
                "listening ssh",
                "SELECT address, port, protocol FROM listening_ports "
                "WHERE port = 22",
                ["listening_ports"],
            ),
            (
                "sshd package",
                "SELECT name, version FROM sysmanage_packages "
                "WHERE name LIKE '%openssh%'",
                ["sysmanage_packages"],
            ),
        ],
    ),
    (
        "privileged-accounts",
        "Local accounts with a login shell and uid 0.",
        [
            (
                "root-equivalent users",
                "SELECT username, uid, shell FROM users WHERE uid = 0",
                ["users"],
            ),
        ],
    ),
    (
        "expiring-certificates",
        "Certificates in the system trust store and where they came from.",
        [
            (
                "trust store",
                "SELECT common_name, issuer, not_valid_after FROM certificates",
                ["certificates"],
            ),
        ],
    ),
]

# Which watched paths each demo host reports, and how. The unreadable and
# absent rows are the POINT of the fixture: without them the comparison
# screenshot shows only differences and never a blind spot.
WATCH_PATHS = [
    ("/etc/ssh/sshd_config", ["linux", "darwin", "freebsd"]),
    ("/etc/sudoers", ["linux", "darwin", "freebsd"]),
    ("/etc/pam.d/common-auth", ["linux"]),
    ("/etc/shadow", ["linux"]),
    ("/etc/login.defs", ["linux"]),
]

FILE_STATE = {
    "ubuntu-web-01.corp.northstar.io": [
        ("/etc/ssh/sshd_config", "present", "9f2b" + "a" * 60, "0644", "root"),
        ("/etc/sudoers", "present", "3c71" + "b" * 60, "0440", "root"),
        ("/etc/pam.d/common-auth", "present", "aa10" + "c" * 60, "0644", "root"),
        ("/etc/shadow", "unreadable", None, None, None),
        ("/etc/login.defs", "present", "5d44" + "d" * 60, "0644", "root"),
    ],
    "rhel-db-01.corp.northstar.io": [
        # Content drift on sshd_config, PERMISSION drift on sudoers with
        # identical content, and login.defs deleted outright.
        ("/etc/ssh/sshd_config", "present", "e881" + "e" * 60, "0644", "root"),
        ("/etc/sudoers", "present", "3c71" + "b" * 60, "0644", "root"),
        ("/etc/pam.d/common-auth", "present", "aa10" + "c" * 60, "0644", "root"),
        ("/etc/shadow", "unreadable", None, None, None),
        ("/etc/login.defs", "absent", None, None, None),
    ],
    "debian-app-01.corp.northstar.io": [
        ("/etc/ssh/sshd_config", "present", "9f2b" + "a" * 60, "0644", "root"),
        ("/etc/sudoers", "present", "3c71" + "b" * 60, "0440", "root"),
        ("/etc/pam.d/common-auth", "present", "aa10" + "c" * 60, "0644", "root"),
        ("/etc/shadow", "unreadable", None, None, None),
        ("/etc/login.defs", "present", "5d44" + "d" * 60, "0644", "root"),
    ],
}


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _wake_demo_hosts(session, hosts, now):
    """Keep the demo fleet looking live through the capture.

    The demo hosts are REST fixtures with no agent behind them, so the
    heartbeat monitor marks them down minutes after seeding and anything
    gated on Host.active then renders empty -- a screenshot that makes the
    feature look broken.
    """
    woken = 0
    for host in hosts.values():
        if host.approval_status != "approved":
            continue
        host.status = "up"
        host.active = True
        host.last_access = now
        woken += 1
    return woken


def _seed_packs(session, now):
    packs = {}
    for name, description, queries in PACKS:
        pack = QueryPack(
            id=uuid.uuid4(),
            name=name,
            description=description,
            enabled=True,
            created_by=AUTHOR,
            created_at=now - timedelta(days=9),
            updated_at=now - timedelta(days=2),
        )
        session.add(pack)
        session.flush()
        for qname, sql, tables in queries:
            session.add(
                QueryPackQuery(
                    id=uuid.uuid4(),
                    pack_id=pack.id,
                    name=qname,
                    sql=sql,
                    required_tables=tables,
                    interval_minutes=60,
                )
            )
        packs[name] = pack
    return packs


def _seed_runs(session, packs, hosts, now):
    """One run per host per pack, graded the way the engine would grade it.

    Windows deliberately grades ``partial``: it has no ``mounts`` and its
    listening-ports provider is unprivileged in the fixture, so it is the host
    that demonstrates not-covered being distinct from failure.
    """
    runs = 0
    for pack in packs.values():
        for index, fqdn in enumerate(DEMO_FQDNS):
            host = hosts.get(fqdn)
            if host is None:
                continue
            not_covered = 1 if fqdn.startswith("win11") else 0
            total = sum(len(q[2]) for q in PACKS if q[0] == pack.name) or 1
            run = QueryPackRun(
                id=uuid.uuid4(),
                pack_id=pack.id,
                host_id=host.id,
                status="partial" if not_covered else "success",
                queries_total=total,
                queries_ok=total - not_covered,
                queries_not_covered=not_covered,
                queries_failed=0,
                contract_version=2,
                started_at=now - timedelta(minutes=40 + index * 3),
                completed_at=now - timedelta(minutes=39 + index * 3),
            )
            session.add(run)
            session.flush()
            if not_covered:
                session.add(
                    QueryPackResultRow(
                        id=uuid.uuid4(),
                        run_id=run.id,
                        query_name="listening ssh",
                        status="not_covered",
                        reason="insufficient_privilege",
                        columns=None,
                        collected_at=run.completed_at,
                    )
                )
            else:
                session.add(
                    QueryPackResultRow(
                        id=uuid.uuid4(),
                        run_id=run.id,
                        query_name=PACKS[0][2][0][0],
                        status="ok",
                        columns={
                            "address": "0.0.0.0",
                            "port": "22",
                            "protocol": "6",
                        },
                        collected_at=run.completed_at,
                    )
                )
            runs += 1
    return runs


def _seed_assignments(session, packs, hosts, now):
    assigned = 0
    for pack in packs.values():
        for fqdn in DEMO_FQDNS[:4]:
            host = hosts.get(fqdn)
            if host is None:
                continue
            session.add(
                QueryPackAssignment(
                    id=uuid.uuid4(),
                    pack_id=pack.id,
                    host_id=host.id,
                    enabled=True,
                    interval_minutes=60,
                    created_by=AUTHOR,
                    created_at=now - timedelta(days=9),
                    last_dispatched_at=now - timedelta(minutes=40),
                )
            )
            assigned += 1
    return assigned


def _seed_file_watches(session, hosts, now):
    watch = FileWatch(
        id=uuid.uuid4(),
        name="CIS Linux config baseline",
        description="Authentication and privilege configuration files.",
        version=1,
        enabled=True,
        created_by=AUTHOR,
        created_at=now - timedelta(days=6),
        updated_at=now - timedelta(days=6),
    )
    session.add(watch)
    session.flush()
    for path, platforms in WATCH_PATHS:
        session.add(
            FileWatchPath(
                id=uuid.uuid4(),
                watch_id=watch.id,
                path=path,
                platforms=platforms,
            )
        )

    states = 0
    for fqdn, rows in FILE_STATE.items():
        host = hosts.get(fqdn)
        if host is None:
            continue
        session.add(
            FileWatchAssignment(
                id=uuid.uuid4(),
                watch_id=watch.id,
                host_id=host.id,
                enabled=True,
                interval_minutes=60,
                created_by=AUTHOR,
                created_at=now - timedelta(days=6),
                last_dispatched_at=now - timedelta(minutes=12),
            )
        )
        for path, state, sha, mode, owner in rows:
            session.add(
                HostFileState(
                    id=uuid.uuid4(),
                    host_id=host.id,
                    path=path,
                    state=state,
                    sha256=sha,
                    size=4096 if state == "present" else None,
                    mode=mode,
                    owner=owner,
                    group_name=owner,
                    mtime=int((now - timedelta(days=3)).timestamp()),
                    type="regular" if state != "absent" else None,
                    collected_at=now - timedelta(minutes=12),
                )
            )
            states += 1
    return states


def main():
    session = sessionmaker(bind=db.get_engine())()
    now = _now()
    try:
        hosts = {
            h.fqdn: h
            for h in session.query(Host).filter(Host.fqdn.in_(DEMO_FQDNS)).all()
        }
        if not hosts:
            print("  no demo hosts present — run make screenshots-seed first")
            return

        awake = _wake_demo_hosts(session, hosts, now)

        # Children before parents.
        for model in (
            HostFileState,
            FileWatchAssignment,
            FileWatchPath,
            FileWatch,
            QueryPackResultRow,
            QueryPackRun,
                    QueryPackAssignment,
            QueryPackQuery,
            QueryPack,
        ):
            session.query(model).delete()

        packs = _seed_packs(session, now)
        session.flush()
        assigned = _seed_assignments(session, packs, hosts, now)
        runs = _seed_runs(session, packs, hosts, now)
        states = _seed_file_watches(session, hosts, now)

        session.commit()
        print(f"    packs: {len(packs)}  assignments: {assigned}  runs: {runs}")
        print(f"    watched-file states: {states}")
        print(f"    demo hosts marked up/active: {awake}")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
