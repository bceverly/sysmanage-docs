#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Seed fleet backups (Phase 24, Community) for the Backups screenshots.

Runs INSIDE the screenshot VM against the sysmanage ORM, like the other
seeders.  Apply via:  make screenshots-backups-seed

WHAT IT HAS TO SHOW, AND WHY
----------------------------
  * One target, served by freebsd-build-01, whose storage path is on UFS and
    is not sealed: the target card's cautions "Not sealed" and "this
    filesystem cannot take snapshots" -- the heads-up the docs describe for
    storage that is not ZFS or btrfs -- next to a healthy storage side (job
    files confirmed, last prune, last metadata check).
  * ubuntu-web-01 "Backed up": 14 daily snapshots, unsigned (Community), and
    a policy with "Leave out" / "Also back up" path patterns -- the policy
    dialog shot opens this host.
  * rhel-db-01 "Backing up": a capture running now, with restate's progress
    (paths and bytes read), pausing PostgreSQL while it reads.
  * debian-app-01 "Failed": the last attempt failed on a stale NFS handle;
    its last successful backup is a day older (the "Last attempt" line).
  * win11-ws-01 and macos-studio-01 "Not equipped -- Not supported on this
    OS"; freebsd-build-01 itself "Not configured" (it is the storage host).

CAPABILITIES: the demo hosts' capability reports predate backups, so the
backup group is added to each EXISTING report (as the discovery and malware
seeds add theirs): equipped on the Linux and FreeBSD hosts, not applicable
on Windows and macOS.  The screenshot admin is granted "Manage Backups" and
"Restore Files" (the migration grants them only to administrators that
existed when it ran).

THE RESTORE PREVIEW: "Preview" asks the host's agent for a dry-run plan, and
the demo hosts have no agent.  So this seeder leaves a small helper running
in the VM for two hours that answers ubuntu-web-01's dry-run restores
through the REAL result ingestion (``backup_results.record_result``) with a
plan for the paths asked -- what the dialog shows is what the product
stored.

THE BACKUP TICK runs every five minutes in the VM.  It skips inactive hosts
(the demo hosts are), and debian-app-01's backup window starts twelve hours
from now, so it is never due during a capture: the "Failed" row cannot turn
into "Backing up" mid-run.

Run AFTER screenshots-seed (demo hosts).  Idempotent: clears its own rows
first.
"""

import json
import os
import signal
# Fixed argv: this interpreter and a file the seeder itself wrote.
import subprocess  # nosec B404
import sys
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from backend.persistence import db
from backend.persistence.models import (
    BackupPolicy,
    BackupRun,
    BackupSnapshot,
    BackupTarget,
    Host,
    SecurityRole,
    User,
    UserSecurityRole,
)

AUTHOR = "admin@sysmanage.org"
DOMAIN = "corp.northstar.io"
RESTATE = "2.1.0.3"
NOW = datetime.now(timezone.utc).replace(tzinfo=None)
GB = 1_000_000_000
ROLES = ("Manage Backups", "Restore Files")
BACKUP_COMMANDS = ("backup_configure", "backup_run", "backup_restore")
EQUIPPED = ("ubuntu-web-01", "rhel-db-01", "debian-app-01", "freebsd-build-01")
WRONG_PLATFORM = ("win11-ws-01", "macos-studio-01")

# The helper answers this host's dry-run restores (see the module docstring).
# Fixed paths inside the disposable screenshot VM only.
ANSWERER = "/tmp/sysmanage-shots-restore-answerer.py"  # nosec B108
ANSWERER_PID = "/tmp/sysmanage-shots-restore-answerer.pid"  # nosec B108
ANSWERER_LOG = "/tmp/sysmanage-shots-restore-answerer.log"  # nosec B108


def _host(session, name):
    return session.query(Host).filter(Host.fqdn == f"{name}.{DOMAIN}").first()


def _repo_dir(host):
    """As backup_jobs.repo_dir() names it: fqdn plus the host id's first 8."""
    return f"{host.fqdn}-{str(host.id).replace('-', '')[:8]}"


def _snap(at):
    return at.strftime("%Y%m%dT%H%M%SZ")


def _clear(session):
    for model in (BackupRun, BackupSnapshot, BackupPolicy, BackupTarget):
        session.query(model).delete()
    session.flush()


def _advertise(host, applicable):
    """Add the backup group to the host's EXISTING capability report."""
    report = json.loads(host.agent_capabilities) if host.agent_capabilities else None
    if not isinstance(report, dict):
        print(f"  note: {host.fqdn} has no capability report; left as it is")
        return
    if applicable:
        report.setdefault("capabilities", [])
        report.setdefault("commands", [])
        if "backup" not in report["capabilities"]:
            report["capabilities"].append("backup")
        for command in BACKUP_COMMANDS:
            if command not in report["commands"]:
                report["commands"].append(command)
        (report.get("unavailable") or {}).pop("backup", None)
    else:
        report.setdefault("not_applicable", {})["backup"] = "wrong_platform"
    host.agent_capabilities = json.dumps(report)


def _grant_roles(session):
    user = session.query(User).filter(User.userid == AUTHOR).first()
    if user is None:
        print(f"  note: {AUTHOR} not found; backup roles not granted")
        return
    for name in ROLES:
        role = session.query(SecurityRole).filter(SecurityRole.name == name).first()
        if role is None:
            print(f"  note: role {name!r} missing (migration q48backups not applied?)")
            continue
        held = (
            session.query(UserSecurityRole)
            .filter(UserSecurityRole.user_id == user.id,
                    UserSecurityRole.role_id == role.id)
            .first()
        )  # fmt: skip
        if held is None:
            session.add(UserSecurityRole(id=uuid.uuid4(), user_id=user.id,
                                         role_id=role.id, granted_at=NOW))  # fmt: skip


def _target(session, storage):
    target = BackupTarget(
        id=uuid.uuid4(), name="nas", host_mount_point="/mnt/backups",
        storage_host_id=storage.id, storage_path="/srv/backups/restate",
        max_concurrent=2, seal_mode="zfs_snapshot", zfs_dataset="zroot/sysmanage-backups/restate",
        service_account="restate",
        storage_fs_type="zfs", storage_fs_mount="/srv/backups/restate",
        storage_fs_checked_at=NOW - timedelta(hours=3), storage_is_btrfs_subvolume=None,
        created_at=NOW - timedelta(days=15), created_by=AUTHOR, updated_at=NOW - timedelta(days=15),
    )  # fmt: skip
    session.add(target)
    session.flush()
    return target


def _finding(code, level="ok", **params):
    return {"code": code, "level": level, "params": params}


def _audit(prepared=True, protected=True):
    """The storage host's check of one repository: the NFS baseline is set
    up; a repository not yet prepared shares the filesystem and has no
    export of its own (the mid-migration picture the target card shows)."""
    found = [_finding(c) for c in ("nfs_server", "nfs_v4", "nfs_v4_only",
                                   "nfs_local_locks", "nfs_v4_root")]  # fmt: skip
    found.append(_finding("service_account", account="restate"))
    if prepared:
        found += [_finding("own_filesystem", type="zfs"), _finding("export_own"),
                  _finding("export_restricted"), _finding("export_mapping")]  # fmt: skip
    else:
        found += [_finding("own_filesystem", "warning", type="zfs"),
                  _finding("export_own", "warning")]  # fmt: skip
    found.append(_finding("append_only_layout") if protected else
                 _finding("append_only_layout", "warning", directories=["packs"],
                          unprotected_files=312))  # fmt: skip
    return found


# pylint: disable-next=too-many-arguments
def _policy(session, target, host, *, keep=None, skip=None, quiesce=(), window=None,
            repository_gb=None, audit=None, hooks=None):  # fmt: skip
    policy = BackupPolicy(
        id=uuid.uuid4(), host_id=host.id, target_id=target.id, enabled=True,
        interval_hours=24, window_start_hour=window, keep_last=14, check_interval_days=7,
        quiesce=bool(quiesce), quiesce_with=json.dumps(list(quiesce)),
        keep_paths=json.dumps(keep or []), skip_paths=json.dumps(skip or []),
        capture_requested_at=None,
        repository_bytes=int(repository_gb * GB) if repository_gb else None,
        config_version=1, host_acked_version=1, storage_acked_version=1,
        restate_version=RESTATE, storage_restate_version=RESTATE,
        storage_protects=True,
        storage_nfs_path=f"/restate/{_repo_dir(host)}",
        available_hooks=json.dumps(hooks) if hooks is not None else None,
        storage_audit=json.dumps(audit or _audit()),
        storage_audit_at=NOW - timedelta(minutes=40),
        created_at=NOW - timedelta(days=15), created_by=AUTHOR, updated_at=NOW - timedelta(days=15),
    )  # fmt: skip
    session.add(policy)
    session.flush()
    return policy


# pylint: disable-next=too-many-arguments
def _run(session, policy, host, action, status, started, minutes, *, result=None,
         message=None, exit_code=0, snapshot=None, progress=None):  # fmt: skip
    finished = started + timedelta(minutes=minutes) if minutes is not None else None
    session.add(BackupRun(
        id=uuid.uuid4(), policy_id=policy.id, host_id=host.id, action=action,
        status=status, exit_code=exit_code if finished else None,
        queued_at=started - timedelta(seconds=20), started_at=started, finished_at=finished,
        result=json.dumps(result) if result is not None else None, snapshot=snapshot,
        progress=json.dumps(progress) if progress else None, message=message,
        restate_version=RESTATE, requested_by="system",
        parameters=json.dumps({"policy_id": str(policy.id), "action": action}),
    ))  # fmt: skip


def _capture(session, policy, host, at, read_gb, new_gb, paths):
    """A good capture, its snapshot row, and the storage side's prune after it."""
    name = _snap(at)
    result = {"schema": 1, "status": "ok", "exit": 0, "snapshot": name,
              "paths": paths, "read_bytes": int(read_gb * GB), "new_bytes": int(new_gb * GB),
              "repository_bytes": policy.repository_bytes, "started_at": at.isoformat() + "Z"}  # fmt: skip
    _run(session, policy, host, "capture", "ok", at, 18, result=result, snapshot=name)
    session.add(BackupSnapshot(
        id=uuid.uuid4(), policy_id=policy.id, host_id=host.id, name=name, created_at=at,
        bytes=int(read_gb * GB), new_bytes=int(new_gb * GB),
        unique_bytes=int(new_gb * GB * 0.6), files=paths, signed=False,
        seen_at=at + timedelta(minutes=18), gone_at=None,
    ))  # fmt: skip


def _storage(session, policy, storage, at, action):
    if action == "prune":
        result = {"schema": 1, "status": "ok", "exit": 0, "removed": 1, "kept": 14}
    elif action == "protect":
        result = {"schema": 1, "status": "ok", "exit": 0, "group": "restate",
                  "files_protected": 4, "snapshots_protected": 1, "unchanged": 2610}  # fmt: skip
    elif action == "seal":
        result = {}
    else:
        result = {"schema": 1, "status": "ok", "exit": 0, "metadata_only": True}
    _run(session, policy, storage, action, "ok", at, 2, result=result)


def _web(session, target, web, storage):
    policy = _policy(
        session, target, web, repository_gb=41.3,
        skip=["/home/*/.local/share/Trash", "**/previews", "/var/www/*/cache"],
        keep=["/home/*/Downloads/contracts"],
        quiesce=("nextcloud",), hooks=["docker", "nextcloud", "postgresql"],
    )  # fmt: skip
    _run(session, policy, storage, "prepare", "ok", NOW - timedelta(days=15, hours=1), 1,
         result={"kind": "zfs"})  # fmt: skip
    for day in range(14, 0, -1):
        at = (NOW - timedelta(days=day - 1, hours=6)).replace(minute=12, second=0)
        _capture(session, policy, web, at, 52.4 + day * 0.02, 0.6 + (day % 3) * 0.2, 188_400 + day)
        _storage(session, policy, storage, at + timedelta(minutes=19), "protect")
        _storage(session, policy, storage, at + timedelta(minutes=21), "seal")
        _storage(session, policy, storage, at + timedelta(minutes=25), "prune")
    _storage(session, policy, storage, NOW - timedelta(hours=20), "check")


def _db(session, target, rhel, storage):
    policy = _policy(session, target, rhel, quiesce=("postgresql",), repository_gb=128.6,
                     audit=_audit(prepared=False), hooks=["postgresql"])  # fmt: skip
    yesterday = NOW - timedelta(hours=26)
    _capture(session, policy, rhel, yesterday, 96.1, 4.2, 61_204)
    _storage(session, policy, storage, yesterday + timedelta(minutes=20), "protect")
    _storage(session, policy, storage, yesterday + timedelta(minutes=22), "seal")
    _storage(session, policy, storage, yesterday + timedelta(minutes=30), "prune")
    _storage(session, policy, storage, yesterday + timedelta(minutes=40), "check")
    progress = {"phase": "walk", "paths": 41_877, "read_bytes": int(38.7 * GB),
                "new_bytes": int(2.9 * GB), "hook": None, "at": NOW.isoformat() + "Z"}  # fmt: skip
    _run(session, policy, rhel, "capture", "running", NOW - timedelta(minutes=34), None,
         progress=progress)  # fmt: skip


def _app(session, target, debian, storage):
    # The window opens twelve hours from now: never due during a capture.
    policy = _policy(session, target, debian, repository_gb=22.8,
                     window=(NOW.hour + 12) % 24,
                     audit=_audit(prepared=False, protected=False))  # fmt: skip
    good = NOW - timedelta(hours=30)
    _capture(session, policy, debian, good, 31.5, 1.1, 97_310)
    # Sealed, but not yet protected: its storage check shows Not append-only.
    _storage(session, policy, storage, good + timedelta(minutes=21), "seal")
    _storage(session, policy, storage, good + timedelta(minutes=25), "prune")
    _storage(session, policy, storage, good + timedelta(minutes=35), "check")
    failed = NOW - timedelta(minutes=55)
    repo = f"/mnt/backups/{_repo_dir(debian)}"
    message = f"{repo}/lock: Stale file handle"
    _run(session, policy, debian, "capture", "failed", failed, 1, exit_code=2,
         result={"schema": 1, "status": "failed", "exit": 2, "message": message},
         message=message)  # fmt: skip


# ---------------------------------------------------------------------------
# the restore-preview answerer (a separate process: the capture takes a while)
# ---------------------------------------------------------------------------

ANSWERER_SOURCE = r'''
"""Answers ubuntu-web-01's dry-run restores for the docs screenshots, through
the real result ingestion.  Written and started by seed_backups.py; exits
after two hours."""
import json, time
from datetime import datetime, timezone
from sqlalchemy.orm import sessionmaker
from backend.persistence import db
from backend.persistence.models import BackupRun, Host
from backend.services import backup_results

PLAN = [
    "/etc/nginx/nginx.conf", "/etc/nginx/conf.d/gzip.conf",
    "/etc/nginx/sites-available/shop.northstar.io",
    "/etc/nginx/sites-available/status.northstar.io",
    "/etc/nginx/sites-enabled/shop.northstar.io",
    "/etc/nginx/sites-enabled/status.northstar.io",
    "/etc/nginx/snippets/ssl-params.conf",
    "/etc/letsencrypt/renewal/shop.northstar.io.conf",
]
SIZE = {p: 900 + 37 * i for i, p in enumerate(PLAN)}
DEADLINE = time.time() + 2 * 3600

def plan_for(include):
    if not include:
        return PLAN
    return [p for p in PLAN if any(p == i or p.startswith(i.rstrip("/") + "/") for i in include)]

Session = sessionmaker(bind=db.get_engine())
while time.time() < DEADLINE:
    s = Session()
    try:
        host = s.query(Host).filter(Host.fqdn == "ubuntu-web-01.corp.northstar.io").first()
        runs = [] if host is None else (
            s.query(BackupRun)
            .filter(BackupRun.host_id == host.id, BackupRun.action == "restore",
                    BackupRun.status.in_(("queued", "running")))
            .all())
        for run in runs:
            params = json.loads(run.parameters or "{}")
            if not params.get("dry_run", True):
                continue
            plan = plan_for(params.get("include") or [])
            now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            backup_results.record_result(s, host.id, {
                "run_id": str(run.id), "policy_id": str(run.policy_id), "action": "restore",
                "status": "ok", "exit": 0, "started_at": now, "finished_at": now,
                "restate_version": "2.0.0.1",
                "result": {"schema": 1, "status": "ok", "exit": 0, "dry_run": True,
                           "files": len(plan), "bytes": sum(SIZE[p] for p in plan),
                           "plan": plan, "plan_count": len(plan), "missing": []},
            })
            s.commit()
            print("answered", run.id, len(plan), flush=True)
    except Exception as err:  # keep answering: the next poll may succeed
        s.rollback()
        print("error", err, flush=True)
    finally:
        s.close()
    time.sleep(2)
'''


def _start_answerer():
    """Replace any earlier helper with a fresh two-hour one."""
    try:
        with open(ANSWERER_PID, encoding="utf-8") as handle:
            os.kill(int(handle.read().strip()), signal.SIGTERM)
    except (OSError, ValueError):
        pass
    with open(ANSWERER, "w", encoding="utf-8") as handle:
        handle.write(ANSWERER_SOURCE)
    with open(ANSWERER_LOG, "w", encoding="utf-8") as log:
        # Not a `with`: the helper must outlive this seeder (its own session).
        # pylint: disable-next=consider-using-with
        proc = subprocess.Popen(  # nosec B603
            [sys.executable, ANSWERER], cwd=os.getcwd(), env=dict(os.environ),
            stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
            start_new_session=True,
        )  # fmt: skip
    with open(ANSWERER_PID, "w", encoding="utf-8") as handle:
        handle.write(str(proc.pid))
    return proc.pid


def main() -> None:
    session = sessionmaker(bind=db.get_engine())()
    try:
        _clear(session)
        hosts = {}
        for name in EQUIPPED + WRONG_PLATFORM:
            host = _host(session, name)
            if host is None:
                print(f"  - skip {name}: demo host not found (run screenshots-seed first)")
                continue
            hosts[name] = host
            _advertise(host, applicable=name in EQUIPPED)
        missing = [n for n in ("freebsd-build-01", "ubuntu-web-01") if n not in hosts]
        if missing:
            print(f"  no {', '.join(missing)} -- run make screenshots-seed first")
            return
        _grant_roles(session)
        storage = hosts["freebsd-build-01"]
        target = _target(session, storage)
        _web(session, target, hosts["ubuntu-web-01"], storage)
        if "rhel-db-01" in hosts:
            _db(session, target, hosts["rhel-db-01"], storage)
        if "debian-app-01" in hosts:
            _app(session, target, hosts["debian-app-01"], storage)
        session.commit()
        pid = _start_answerer()
        print(f"  + backup target on {storage.fqdn}, {session.query(BackupPolicy).count()} "
              f"policies, {session.query(BackupSnapshot).count()} snapshots; "
              f"restore-preview helper running (pid {pid}, two hours)")
    finally:
        session.close()


if __name__ == "__main__":
    main()
