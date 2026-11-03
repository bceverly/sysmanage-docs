#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Seed the Professional+ backup features (ROADMAP 24.6 / 24.7) for the
Professional pass's Backups shots.

Runs INSIDE the Professional (and Enterprise) screenshot VM against the
sysmanage ORM, AFTER seed_backups.py and seed_cloud_backup.py: it builds on
their target, policies and snapshots.  Apply via:
make screenshots-backups-pro-seed

WHAT IT HAS TO SHOW, AND WHY
----------------------------
  * Encryption: rhel-db-01 encrypted 60 days ago and its key rotated 20 days
    ago (two keys kept for restores; the next rotation from the default
    365-day schedule), its earlier plain repository still restorable.
    debian-app-01 encrypted 3 days ago.
  * Break-glass escrow: an escrow public key saved on the target, and an
    export 6 days ago that holds rhel-db-01's keys -- so it covers 1 of the 2
    encrypted hosts and is STALE (debian-app-01 came after it): the Backups
    page banner and the Encryption panel's warning.
  * Snapshot signing on for the target since 10 days ago; the snapshots taken
    since are signed.
  * ubuntu-web-01: grandfather-father-son retention (7 last, 14 daily, 8
    weekly, 6 monthly) over six months of snapshots, so "Preview the next
    prune" removes some; full-read verification every 30 days, last passed 9
    days ago; a drift timeline over its last two weeks (package upgrades and
    the file changes no package explains); its OWN policy while the tag
    policy "Production servers" also covers it -- the card offers "Use the
    tag policy".
  * Tag policies: "Production servers" (tag production, priority 10), which
    rhel-db-01 follows ("From tag policy Production servers (priority 10)"),
    and "Staging" (tag staging, priority 50).  rhel-db-01's settings are put
    on it with the server's own apply_settings, so the backup tick's resolver
    finds nothing to change.

The audit rows for the export are written as the engine writes them (one per
host, "Backup keys exported (break-glass)"), with the audit service's own
per-entry integrity hash, dated 6 days ago.

Idempotent: seed_backups.py clears the keys, diffs and tag policies; this
seeder clears its audit rows.
"""

import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from backend.persistence import db
from backend.persistence.models import (
    AuditLog,
    BackupPolicy,
    BackupPolicyKey,
    BackupRun,
    BackupSnapshot,
    BackupSnapshotDiff,
    BackupTagPolicy,
    BackupTarget,
    Host,
    Tag,
    User,
)
from backend.services import backup_tag_policies

AUTHOR = "admin@sysmanage.org"
DOMAIN = "corp.northstar.io"
NOW = datetime.now(timezone.utc).replace(tzinfo=None)
GB = 1_000_000_000
BREAK_GLASS_AUDIT = "Backup keys exported (break-glass)"
DEMO_KEY = "-----BEGIN PGP PUBLIC KEY BLOCK-----\n(demo)\n-----END PGP PUBLIC KEY BLOCK-----\n"
SIGN_FINGERPRINT = "9C4E2A1B7D3F60E8A5B21C9D4F7E3A0B6C8D1E2F"
ESCROW_FINGERPRINT = "3B7D9E1F2A4C6E8B0D1F3A5C7E9B2D4F6A8C0E1B"
ESCROW_UID = "Northstar backup escrow <backup-escrow@corp.northstar.io>"
SIGNING_DAYS = 10
EXPORT_DAYS = 6
PRODUCTION = {
    "enabled": True, "interval_hours": 24, "window_start_hour": 1, "keep_last": 14,
    "check_interval_days": 7, "quiesce": True, "keep_daily": 7, "keep_weekly": 4,
    "keep_monthly": 12, "keep_yearly": 0, "verify_interval_days": 30,
    "quiesce_with": ["postgresql"], "keep_paths": [], "skip_paths": ["/var/cache/*"],
}  # fmt: skip
STAGING = dict(PRODUCTION, keep_last=7, keep_monthly=3, verify_interval_days=0,
               quiesce=False, quiesce_with=[])  # fmt: skip


def _host(session, name):
    return session.query(Host).filter(Host.fqdn == f"{name}.{DOMAIN}").first()


def _policy(session, host):
    if host is None:
        return None
    return session.query(BackupPolicy).filter(BackupPolicy.host_id == host.id).first()


def _repo_dir(host):
    """As backup_jobs.repo_dir() names it: fqdn plus the host id's first 8."""
    return f"{host.fqdn}-{str(host.id).replace('-', '')[:8]}"


def _fingerprint(seed):
    """A made-up OpenPGP fingerprint for the demo: 40 hex digits, stable per seed."""
    return hashlib.sha256(seed.encode()).hexdigest()[:40].upper()


def _snap(at):
    return at.strftime("%Y%m%dT%H%M%SZ")


# ---------------------------------------------------------------------------
# encryption, rotation, signing, escrow
# ---------------------------------------------------------------------------


def _encrypt(session, host, policy, days, rotated_days=None):
    """The policy as backup_engine leaves it: a new, encrypted repository,
    the plain one kept, and a key row per key it has held."""
    encrypted = NOW - timedelta(days=days)
    first = _fingerprint(f"{host.fqdn} key 1")
    keys = [(first, encrypted)]
    if rotated_days is not None:
        keys.append((_fingerprint(f"{host.fqdn} key 2"), NOW - timedelta(days=rotated_days)))
    for index, (fingerprint, made) in enumerate(keys):
        replaced = keys[index + 1][1] if index + 1 < len(keys) else None
        session.add(BackupPolicyKey(
            id=uuid.uuid4(), policy_id=policy.id, fingerprint=fingerprint,
            subkey_id=fingerprint[-16:], created_at=made, replaced_at=replaced,
            key_ref=f"secret/data/sysmanage/backup-keys/{policy.id}/{fingerprint[-16:]}",
        ))  # fmt: skip
    current = keys[-1][0]
    policy.encrypt_public_key = DEMO_KEY
    policy.encrypt_fingerprint = current
    policy.encrypt_key_ref = f"secret/data/sysmanage/backup-keys/{policy.id}/{current[-16:]}"
    policy.encrypted_at = encrypted
    policy.encrypt_rotated_at = keys[-1][1] if rotated_days is not None else None
    policy.previous_repository_dir = _repo_dir(host)
    policy.repository_dir = f"{_repo_dir(host)}-enc"
    # Captures since encryption went to the new repository.
    for snapshot in session.query(BackupSnapshot).filter(BackupSnapshot.policy_id == policy.id):
        if snapshot.created_at and snapshot.created_at >= encrypted:
            snapshot.repository_dir = policy.repository_dir


def _target_keys(target):
    target.key_rotation_days = None  # the default schedule (365 days)
    target.sign_public_key = DEMO_KEY
    target.sign_fingerprint = SIGN_FINGERPRINT
    target.sign_key_ref = "secret/data/sysmanage/backup-signing/target"
    target.signing_enabled_at = NOW - timedelta(days=SIGNING_DAYS)
    target.escrow_public_key = DEMO_KEY
    target.escrow_fingerprint = ESCROW_FINGERPRINT
    target.escrow_uid = ESCROW_UID
    target.escrow_saved_at = NOW - timedelta(days=EXPORT_DAYS, minutes=5)
    target.escrow_saved_by = AUTHOR


def _sign_snapshots(session):
    since = NOW - timedelta(days=SIGNING_DAYS)
    for snapshot in session.query(BackupSnapshot).filter(BackupSnapshot.created_at >= since):
        snapshot.signed = True
        snapshot.signer = SIGN_FINGERPRINT


def _export_audit(session, host):
    """One "Backup keys exported (break-glass)" entry, as the engine writes
    it, with the audit service's integrity hash -- dated EXPORT_DAYS ago."""
    # pylint: disable-next=import-outside-toplevel
    from backend.services.audit_service import ActionType, EntityType, Result

    user = session.query(User).filter(User.userid == AUTHOR).first()
    entry_id = uuid.uuid4()
    when = NOW - timedelta(days=EXPORT_DAYS)
    user_id = user.id if user else None
    parts = [str(entry_id), str(when), str(user_id), ActionType.UPDATE.value,
             EntityType.HOST.value, str(host.id), BREAK_GLASS_AUDIT, Result.SUCCESS.value]  # fmt: skip
    session.add(AuditLog(
        id=entry_id, timestamp=when, user_id=user_id, username=AUTHOR,
        action_type=ActionType.UPDATE.value, entity_type=EntityType.HOST.value,
        entity_id=str(host.id), entity_name=host.fqdn, description=BREAK_GLASS_AUDIT,
        details={"recipient": ESCROW_FINGERPRINT, "reason": "Quarterly break-glass drill"},
        result=Result.SUCCESS.value,
        integrity_hash=hashlib.sha256("|".join(parts).encode()).hexdigest(),
    ))  # fmt: skip


# ---------------------------------------------------------------------------
# ubuntu-web-01: retention, verification, drift
# ---------------------------------------------------------------------------


def _older_snapshots(session, policy, host):
    """Six months of snapshots before the two weeks seed_backups.py made, so
    the retention preview has something to remove."""
    for day in range(15, 181, 3):
        at = (NOW - timedelta(days=day, hours=6)).replace(minute=12, second=0)
        session.add(BackupSnapshot(
            id=uuid.uuid4(), policy_id=policy.id, host_id=host.id, name=_snap(at),
            created_at=at, bytes=int(52.1 * GB), new_bytes=int(0.7 * GB),
            unique_bytes=int(0.4 * GB), files=188_100 + day, signed=False,
            seen_at=at + timedelta(minutes=18), gone_at=None,
        ))  # fmt: skip


def _verify_run(session, policy, host):
    at = NOW - timedelta(days=9, hours=3)
    session.add(BackupRun(
        id=uuid.uuid4(), policy_id=policy.id, host_id=host.id, action="verify",
        status="ok", exit_code=0, queued_at=at - timedelta(seconds=20), started_at=at,
        finished_at=at + timedelta(minutes=47), requested_by="system",
        result=json.dumps({"schema": 1, "status": "ok", "exit": 0, "read_all": True}),
        parameters=json.dumps({"policy_id": str(policy.id), "action": "verify"}),
    ))  # fmt: skip


def _pkg(change, name, before=None, after=None):
    return {"change": change, "manager": "apt", "name": name, "from": before, "to": after}


def _file(change, path, what="content"):
    return {"change": change, "path": path, "what": what}


# The newest comparisons first: what an operator reads in the timeline.
DRIFT = (
    ([_pkg("U", "openssl", "3.0.13-0ubuntu3.4", "3.0.13-0ubuntu3.5"),
      _pkg("U", "libssl3t64", "3.0.13-0ubuntu3.4", "3.0.13-0ubuntu3.5")],
     [_file("M", "/etc/nginx/sites-available/shop.northstar.io"),
      _file("A", "/etc/nginx/snippets/rate-limit.conf"),
      _file("M", "/var/log/nginx/access.log"), _file("M", "/var/log/syslog")], 14),
    ([_pkg("I", "jq", None, "1.7.1-3build1")],
     [_file("M", "/etc/cron.d/certbot"), _file("D", "/home/deploy/.ssh/authorized_keys.bak"),
      _file("M", "/home/deploy/.cache/pip/http/selfcheck.json")], 6),
    ([],
     [_file("M", "/etc/ssh/sshd_config"), _file("M", "/etc/ssh/sshd_config", "mode"),
      _file("M", "/var/log/auth.log")], 0),
)
QUIET = ([], [_file("M", "/var/log/syslog"), _file("M", "/var/cache/apt/pkgcache.bin")], 0)


def _count(changes, kind):
    return sum(1 for change in changes if change["change"] == kind)


def _drift(session, policy, host):
    names = [row.name for row in session.query(BackupSnapshot)
             .filter(BackupSnapshot.policy_id == policy.id,
                     BackupSnapshot.created_at >= NOW - timedelta(days=14))
             .order_by(BackupSnapshot.name)]  # fmt: skip
    pairs = list(zip(names, names[1:]))[::-1]  # newest first
    for index, (before, after) in enumerate(pairs):
        packages, changes, explained = DRIFT[index] if index < len(DRIFT) else QUIET
        session.add(BackupSnapshotDiff(
            id=uuid.uuid4(), policy_id=policy.id, host_id=host.id, from_snapshot=before,
            to_snapshot=after, status="ok", added=_count(changes, "A"),
            deleted=_count(changes, "D"), modified=_count(changes, "M"), packages_changed=len(packages), explained=explained,
            changes=json.dumps(changes), packages=json.dumps(packages),
            truncated=False, packages_truncated=False,
            computed_at=datetime.strptime(after, "%Y%m%dT%H%M%SZ") + timedelta(minutes=25),
        ))  # fmt: skip


def _ubuntu(session, host):
    policy = _policy(session, host)
    if policy is None:
        print("  note: ubuntu-web-01 has no policy (run seed_backups.py first)")
        return
    policy.keep_last, policy.keep_daily, policy.keep_weekly, policy.keep_monthly = 7, 14, 8, 6
    policy.verify_interval_days = 30
    _older_snapshots(session, policy, host)
    _verify_run(session, policy, host)
    session.flush()
    _drift(session, policy, host)


# ---------------------------------------------------------------------------
# tag policies
# ---------------------------------------------------------------------------


def _tag_policies(session, rhel):
    made = {}
    for priority, (name, tag_name, settings) in enumerate(
        (("Production servers", "production", PRODUCTION), ("Staging", "staging", STAGING))
    ):  # fmt: skip
        tag = session.query(Tag).filter(Tag.name == tag_name).first()
        if tag is None:
            print(f"  note: tag {tag_name!r} missing (run screenshots-seed first); "
                  f"tag policy {name!r} not made")
            continue
        row = BackupTagPolicy(
            id=uuid.uuid4(), name=name, tag_id=tag.id, priority=10 + 40 * priority,
            enabled=True, settings=json.dumps(settings),
            created_at=NOW - timedelta(days=12 - priority), created_by=AUTHOR,
            updated_at=NOW - timedelta(days=12 - priority),
        )  # fmt: skip
        session.add(row)
        made[name] = row
    session.flush()
    policy = _policy(session, rhel)
    if policy is not None and "Production servers" in made:
        backup_tag_policies.apply_settings(policy, PRODUCTION)
        policy.tag_policy_id = made["Production servers"].id


def main() -> None:
    session = sessionmaker(bind=db.get_engine())()
    try:
        session.query(AuditLog).filter(AuditLog.description == BREAK_GLASS_AUDIT).delete()
        target = session.query(BackupTarget).first()
        ubuntu, rhel, debian = (_host(session, n) for n in
                                ("ubuntu-web-01", "rhel-db-01", "debian-app-01"))  # fmt: skip
        if target is None or _policy(session, rhel) is None:
            print("  no backup target or rhel-db-01 policy -- run screenshots-backups-seed first")
            return
        _target_keys(target)
        _encrypt(session, rhel, _policy(session, rhel), 60, rotated_days=20)
        if _policy(session, debian) is not None:
            _encrypt(session, debian, _policy(session, debian), 3)
        _export_audit(session, rhel)
        _ubuntu(session, ubuntu)
        _sign_snapshots(session)
        _tag_policies(session, rhel)
        session.commit()
        print(f"  + Pro+ backups: rhel-db-01 + debian-app-01 encrypted, escrow export covering "
              f"1 of 2 (stale), signing on, {session.query(BackupSnapshotDiff).count()} drift "
              f"comparisons, {session.query(BackupTagPolicy).count()} tag policies")
    finally:
        session.close()


if __name__ == "__main__":
    main()
