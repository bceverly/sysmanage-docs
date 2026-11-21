#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Seed the Enterprise backup operations (ROADMAP 27.3) for the Backup
Operations page's shots: restore readiness, four-eyes approval of restores
and legal holds (27.1 / 27.2), several targets, an off-site copy, a host
moving with its backups, and a moved host whose old repository is still kept.

Runs INSIDE the Enterprise screenshot VM against the sysmanage ORM, AFTER
seed_backups.py and seed_backups_pro.py: it builds on their target ("nas" on
freebsd-build-01), policies and snapshots.  Apply via:
make screenshots-backups-ent-seed

WHAT IT HAS TO SHOW, AND WHY
----------------------------
  * Three targets.  "nas" (location HQ, the default) copies off-site to
    "Offsite" (location DC2, restate-proxy on ubuntu-ws-07, another storage
    host, btrfs seals kept 30 days), whose card says it holds nas's off-site
    copies -- and nas's card that its off-site copy is immutable.  The
    off-site storage host is given the backup capability (its demo report
    has none), as seed_backups.py does for its storage host.  "nas-2" (HQ,
    restate-proxy) is a second target on nas's own storage host.
  * ubuntu-web-01's off-site copy on Offsite: every snapshot but the newest
    copied (one to copy), its newest copied snapshot a day old, and readable
    by the host (its agent reports ``offsite_read`` and its read token is in
    the copy's grant) -- so the restore dialog offers "Restore from: Off-site
    copy at Offsite".
  * rhel-db-01 moving from nas to nas-2 (the same storage host): five
    snapshots, three copied -- "Moving to nas-2: snapshots copied 3 of 5"
    with Cancel move.  Four older snapshots are added for it here.
  * debian-app-01 moved from nas-2 to nas three days ago: "Moved from nas-2;
    its old repository there is kept until ..." with Remove now and Keep.

  * Restore readiness: debian-app-01's recovery point objective cut to 24
    hours, so its last good backup (30 hours ago) shows "Recovery point
    missed" beside ubuntu-web-01's proven, recent backups.
  * Four-eyes approval on, with one in-place restore of debian-app-01's
    /etc/nginx waiting for approval -- asked for by another user, so the
    screenshot admin sees Approve and restore and Reject -- one approved
    yesterday and one rejected two days ago.
  * Legal holds: two in force (an older ubuntu-web-01 snapshot for a
    matter, rhel-db-01's latest for an audit) and one released last week.

The policy dialog shot opens ubuntu-web-01 and picks nas-2, which shows the
note that a host with backups is copied first.

THE BACKUP TICK runs every five minutes in the VM and must not act on any of
this mid-capture: the off-site copy and the move copied an hour ago (the
replica tick waits RETRY_HOURS before copying again) and their job files are
acknowledged; the move still has snapshots to copy, so it is never checked
or switched; the kept repository's date is eleven days away, so it is never
removed.

Idempotent: clears its own rows (moves, off-site copies, the two targets it
adds and rhel-db-01's added snapshots) first; seed_backups.py clears them too.
"""

import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from backend.config import settings_service
from backend.persistence import db
from backend.persistence.models import (
    BackupLegalHold,
    BackupMove,
    BackupPolicy,
    BackupReplica,
    BackupRestoreRequest,
    BackupSnapshot,
    BackupTarget,
    Host,
)

AUTHOR = "admin@sysmanage.org"
DOMAIN = "corp.northstar.io"
NOW = datetime.now(timezone.utc).replace(tzinfo=None)
GB = 1_000_000_000
STORAGE = "freebsd-build-01"
OFFSITE_STORAGE = "ubuntu-ws-07"
OFFSITE = "Offsite"
NAS2 = "nas-2"
ADDED = (OFFSITE, NAS2)
# What restate 2.2 and this agent report beyond the 2.0 contract, plus the
# off-site read (27.3).
READ_ABILITY = "offsite_read"
BACKUP_COMMANDS = ("backup_configure", "backup_run", "backup_restore")
GRACE_DAYS = 14
MOVED_DAYS = 3
FOUR_EYES = "backup_four_eyes"
REQUESTER = "dana.ortiz@corp.northstar.io"


def _host(session, name):
    return session.query(Host).filter(Host.fqdn == f"{name}.{DOMAIN}").first()


def _repo_dir(host):
    """As backup_jobs.repo_dir() names it: fqdn plus the host id's first 8."""
    return f"{host.fqdn}-{str(host.id).replace('-', '')[:8]}"


def _policy(session, host):
    return session.query(BackupPolicy).filter(BackupPolicy.host_id == host.id).first()


def _snap(at):
    return at.strftime("%Y%m%dT%H%M%SZ")


def _hash(seed):
    return hashlib.sha256(seed.encode()).hexdigest()


def _clear(session):
    session.query(BackupLegalHold).delete()
    session.query(BackupRestoreRequest).delete()
    session.query(BackupMove).delete()
    session.query(BackupReplica).delete()
    session.flush()
    for target in session.query(BackupTarget).all():
        target.replica_target_id = None
    session.flush()
    for target in session.query(BackupTarget).filter(BackupTarget.name.in_(ADDED)):
        session.delete(target)  # no policy is on them: only moves name them
    rhel = _host(session, "rhel-db-01")
    policy = _policy(session, rhel) if rhel else None
    if policy is not None:  # seed_backups.py gives it one snapshot; keep that
        names = _names(session, policy)
        session.query(BackupSnapshot).filter(
            BackupSnapshot.policy_id == policy.id, BackupSnapshot.name.in_(names[:-1])
        ).delete(synchronize_session=False)
    session.flush()


def _advertise(host):
    """Add the backup group to the host's EXISTING capability report, as
    seed_backups.py does (the off-site storage host runs storage jobs)."""
    report = json.loads(host.agent_capabilities) if host.agent_capabilities else None
    if not isinstance(report, dict):
        print(f"  note: {host.fqdn} has no capability report; left as it is")
        return
    report.setdefault("capabilities", [])
    report.setdefault("commands", [])
    if "backup" not in report["capabilities"]:
        report["capabilities"].append("backup")
    for command in BACKUP_COMMANDS:
        if command not in report["commands"]:
            report["commands"].append(command)
    (report.get("unavailable") or {}).pop("backup", None)
    (report.get("not_applicable") or {}).pop("backup", None)
    host.agent_capabilities = json.dumps(report)


def _target(session, name, storage, path, **extra):
    target = BackupTarget(
        id=uuid.uuid4(), name=name, host_mount_point=f"/mnt/{name.lower()}",
        storage_host_id=storage.id, storage_path=path, max_concurrent=2,
        service_account="restate", is_default=False,
        created_at=NOW - timedelta(days=12), created_by=AUTHOR,
        updated_at=NOW - timedelta(days=12), **extra,
    )  # fmt: skip
    session.add(target)
    session.flush()
    return target


def _proxy(host_name):
    return {"transport": "proxy", "proxy_host": f"{host_name}.{DOMAIN}",
            "proxy_port": 8443, "proxy_pin_sha256": _hash(host_name)}  # fmt: skip


def _names(session, policy):
    return [
        name
        for (name,) in session.query(BackupSnapshot.name)
        .filter(BackupSnapshot.policy_id == policy.id, BackupSnapshot.gone_at.is_(None))
        .order_by(BackupSnapshot.name)
        .all()
    ]


def _offsite_copy(session, web, offsite):
    """ubuntu-web-01's copy on Offsite: all but the newest snapshot, readable."""
    policy = _policy(session, web)
    abilities = json.loads(policy.host_abilities or "[]")
    if READ_ABILITY not in abilities:
        policy.host_abilities = json.dumps(abilities + [READ_ABILITY])
    copied = _names(session, policy)[:-1]
    newest = session.query(BackupSnapshot).filter(
        BackupSnapshot.policy_id == policy.id, BackupSnapshot.name == copied[-1]
    ).first()
    session.add(BackupReplica(
        id=uuid.uuid4(), policy_id=policy.id, target_id=offsite.id,
        repo_dir=_repo_dir(web), config_version=1, acked_version=1,
        prepared_at=NOW - timedelta(days=12), token_sha256=_hash("copy-web"),
        read_token_sha256=_hash("read-web"), snapshots=json.dumps(copied),
        pruned=json.dumps([]), newest_snapshot=newest.name, newest_at=newest.created_at,
        repository_bytes=int(39.6 * GB), last_copy_at=NOW - timedelta(hours=1),
        last_copy_status="ok", abilities=json.dumps(["keep_snapshot"]),
        created_at=NOW - timedelta(days=12), updated_at=NOW - timedelta(hours=1),
    ))  # fmt: skip
    return len(copied)


def _older_snapshots(session, rhel, policy):
    """Four nightly snapshots before rhel-db-01's latest one."""
    for day in range(5, 1, -1):
        at = (NOW - timedelta(days=day, hours=2)).replace(minute=4, second=0)
        session.add(BackupSnapshot(
            id=uuid.uuid4(), policy_id=policy.id, host_id=rhel.id, name=_snap(at),
            created_at=at, bytes=int(95.2 * GB), new_bytes=int(3.8 * GB),
            unique_bytes=int(2.1 * GB), files=61_100 + day, signed=False,
            seen_at=at + timedelta(minutes=20), gone_at=None,
        ))  # fmt: skip
    session.flush()


def _move(session, policy, host, frm, to, **state):
    stamp = state.pop("created_at")
    row = BackupMove(
        id=uuid.uuid4(), policy_id=policy.id, target_id=to.id, from_target_id=frm.id,
        repo_dir=_repo_dir(host), config_version=1, acked_version=1,
        prepared_at=stamp + timedelta(minutes=2), token_sha256=_hash(f"move-{host.fqdn}"),
        abilities=json.dumps(["keep_snapshot"]), created_by=AUTHOR,
        created_at=stamp, **state,
    )  # fmt: skip
    session.add(row)
    return row


def _moving(session, rhel, nas, nas2):
    """rhel-db-01 on its way from nas to nas-2: three of five copied."""
    policy = _policy(session, rhel)
    _older_snapshots(session, rhel, policy)
    names = _names(session, policy)
    started = NOW - timedelta(hours=2)
    _move(session, policy, rhel, nas, nas2, status="copying",
          snapshots=json.dumps(names[:3]), pruned=json.dumps([]),
          repository_bytes=int(84.3 * GB), last_copy_at=NOW - timedelta(hours=1),
          last_copy_status="ok", created_at=started,
          updated_at=NOW - timedelta(hours=1))  # fmt: skip
    return len(names)


def _moved(session, debian, nas, nas2):
    """debian-app-01 moved from nas-2 to nas; the old repository is kept."""
    policy = _policy(session, debian)
    switched = NOW - timedelta(days=MOVED_DAYS)
    _move(session, policy, debian, nas2, nas, status="switched",
          snapshots=json.dumps(_names(session, policy)), pruned=json.dumps([]),
          repository_bytes=int(22.8 * GB), last_copy_at=switched - timedelta(minutes=6),
          last_copy_status="ok", verified_at=switched - timedelta(minutes=1),
          switched_at=switched, keep_until=switched + timedelta(days=GRACE_DAYS),
          created_at=switched - timedelta(minutes=40), updated_at=switched)  # fmt: skip


def _restore_body(snapshot, paths, in_place):
    """As the API stores a held restore (its RestoreBody, JSON)."""
    return json.dumps({
        "snapshot": snapshot, "include": paths, "exclude": [], "dry_run": False,
        "acknowledge_unsigned": True, "in_place": in_place,
        "acknowledge_in_place": in_place, "packages": False,
        "acknowledge_packages": False, "offsite": False,
    })  # fmt: skip


def _approvals(session, hosts):
    """Four-eyes on; one restore waiting, one approved, one rejected."""
    settings_service.set_setting(FOUR_EYES, True)
    debian, web = hosts["debian-app-01"], hosts["ubuntu-web-01"]
    rows = (
        (debian, _names(session, _policy(session, debian))[-1], ["/etc/nginx"],
         "pending", NOW - timedelta(hours=2), None, None),
        (web, _names(session, _policy(session, web))[-2], ["/var/www/shop"],
         "approved", NOW - timedelta(hours=27), AUTHOR, None),
        (web, _names(session, _policy(session, web))[-4], ["/etc"],
         "rejected", NOW - timedelta(days=2, hours=3), AUTHOR,
         "Too broad: name the files under /etc that need putting back"),
    )  # fmt: skip
    for host, snapshot, paths, status, asked, decider, why in rows:
        session.add(BackupRestoreRequest(
            id=uuid.uuid4(), host_id=host.id, body=_restore_body(snapshot, paths, True),
            status=status, requested_by=REQUESTER, requested_at=asked,
            decided_by=decider, decided_at=asked + timedelta(minutes=40) if decider else None,
            reason=why,
        ))  # fmt: skip


def _holds(session, hosts):
    """Two holds in force, one released last week."""
    web, rhel = hosts["ubuntu-web-01"], hosts["rhel-db-01"]
    web_names = _names(session, _policy(session, web))
    rows = (
        (web, web_names[2], "Matter 2026-117 (Northstar v. Acme Logistics)",
         "Litigation hold: keep the web server as it was in early November",
         NOW - timedelta(days=9), None),
        (rhel, _names(session, _policy(session, rhel))[-1], "Internal audit IA-42",
         "Year-end financial audit: keep the database as of the last close",
         NOW - timedelta(days=1), None),
        (web, web_names[5], "Jordan Lee (HR inquiry)",
         "Preserve the shared files while the inquiry is open",
         NOW - timedelta(days=20), NOW - timedelta(days=6)),
    )  # fmt: skip
    for host, snapshot, owner, why, placed, released in rows:
        session.add(BackupLegalHold(
            id=uuid.uuid4(), policy_id=_policy(session, host).id, host_id=host.id,
            snapshot=snapshot, owner=owner, reason=why, placed_by=AUTHOR,
            placed_at=placed, released_by=AUTHOR if released else None,
            released_at=released,
        ))  # fmt: skip


def main() -> None:
    session = sessionmaker(bind=db.get_engine())()
    try:
        _clear(session)
        hosts = {n: _host(session, n) for n in (STORAGE, OFFSITE_STORAGE, "ubuntu-web-01",
                                                "rhel-db-01", "debian-app-01")}  # fmt: skip
        missing = [n for n, h in hosts.items() if h is None]
        nas = session.query(BackupTarget).filter(BackupTarget.name == "nas").first()
        if missing or nas is None or _policy(session, hosts["ubuntu-web-01"]) is None:
            print(f"  missing {', '.join(missing) or 'the nas target'} -- run "
                  "make screenshots-seed and screenshots-backups-seed first")
            return
        nas.is_default, nas.location = True, "HQ"
        _advertise(hosts[OFFSITE_STORAGE])
        offsite = _target(session, OFFSITE, hosts[OFFSITE_STORAGE], "/srv/offsite/restate",
                          location="DC2", seal_mode="btrfs_snapshot",
                          btrfs_snapshot_dir="/srv/offsite/seals", seal_keep_days=30,
                          storage_fs_type="btrfs", storage_fs_mount="/srv/offsite",
                          storage_fs_checked_at=NOW - timedelta(hours=2),
                          storage_is_btrfs_subvolume=True,
                          **_proxy(OFFSITE_STORAGE))  # fmt: skip
        nas2 = _target(session, NAS2, hosts[STORAGE], "/srv/backups2/restate",
                       location="HQ", seal_mode="none", **_proxy(STORAGE))  # fmt: skip
        nas.replica_target_id = offsite.id
        copied = _offsite_copy(session, hosts["ubuntu-web-01"], offsite)
        total = _moving(session, hosts["rhel-db-01"], nas, nas2)
        _moved(session, hosts["debian-app-01"], nas, nas2)
        _policy(session, hosts["debian-app-01"]).rpo_hours = 24  # Recovery point missed
        _approvals(session, hosts)
        _holds(session, hosts)
        session.commit()
        print(f"  + targets nas (default, off-site copy to {OFFSITE}), {OFFSITE} (DC2), {NAS2}; "
              f"ubuntu-web-01's off-site copy holds {copied} snapshots; rhel-db-01 moving "
              f"to {NAS2} (3 of {total}); debian-app-01 moved from {NAS2}, old repository kept; "
              "four-eyes on with one restore waiting; two legal holds in force, one released")
    finally:
        session.close()


if __name__ == "__main__":
    main()
