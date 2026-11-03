#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Seed iCloud Photos backup (ROADMAP 24.12, Community) for the Backups page.

Runs INSIDE the screenshot VM against the sysmanage ORM, right after
seed_backups.py (it needs that seeder's backup target and storage host).
Apply via:  make screenshots-backups-seed

WHAT IT HAS TO SHOW
-------------------
  * The "Cloud backup" section with iCloud backup ENABLED on the storage host
    (freebsd-build-01): the pinned icloudpd version and where the photos are
    kept under the storage path.
  * One account in each state the table can show:
      - Alex Rivera   Up to date: last run 37 new, the rest already present;
      - Sam Chen      Running: a download in progress (its progress line);
      - Jordan Lee    Waiting for the two-factor code: the "Enter code"
                      button the code-dialog shot presses;
      - Priya Patel   Needs sign-in: Apple's sign-in ran out;
      - Morgan Diaz   Failed: Advanced Data Protection without web access,
                      and "Deletes from iCloud after download" set.

The storage host is inactive in the VM, so the cloud tick starts nothing; the
running and waiting jobs report "now", so its stuck-job reaper (3 hours
silent, 12 hours waiting) leaves them alone for the whole capture.

SEED_BACKUPS_ALT=1 (make screenshots-backups-alt) leaves iCloud backup NOT
enabled and no accounts, for the "Enable iCloud backup" shot.

Idempotent: clears its own rows first.
"""

import json
import os
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from backend.persistence import db
from backend.persistence.models import (
    BackupTarget,
    CloudBackupAccount,
    CloudBackupEnable,
    CloudBackupRun,
    Host,
)

AUTHOR = "admin@sysmanage.org"
NOW = datetime.now(timezone.utc).replace(tzinfo=None)
GB = 1_000_000_000
ICLOUDPD = "1.32.3"  # the agent's pinned version (cloud_backup/tool.py)
ALT = os.environ.get("SEED_BACKUPS_ALT", "").strip().lower() in ("1", "true", "yes")

# (name, Apple ID, state, days since sign-in, last good hours ago, photos,
#  GB stored, auto-delete)
ACCOUNTS = (
    ("Alex Rivera", "alex.rivera@example.com", "ok", 20, 5, 18_432, 96.4, False),
    ("Sam Chen", "sam.chen@example.com", "running", 41, 26, 9_210, 41.7, False),
    ("Jordan Lee", "jordan.lee@example.com", "waiting_code", None, None, None, None, False),
    ("Priya Patel", "priya.patel@example.com", "needs_sign_in", 61, 50, 27_905, 158.2, False),
    ("Morgan Diaz", "morgan.diaz@example.com", "failed", 12, 75, 4_388, 19.6, True),
)


def _clear(session):
    for model in (CloudBackupRun, CloudBackupAccount, CloudBackupEnable):
        session.query(model).delete()
    session.flush()


def _enable(session, target, storage):
    session.add(CloudBackupEnable(
        id=uuid.uuid4(), target_id=target.id, host_id=storage.id, status="ok",
        tool_version=ICLOUDPD, install_method="pip",
        cloud_root=f"{target.storage_path}/cloud-photos",
        requested_by=AUTHOR, requested_at=NOW - timedelta(days=21, minutes=4),
        finished_at=NOW - timedelta(days=21),
    ))  # fmt: skip


# pylint: disable-next=too-many-arguments
def _run(session, account, storage, action, status, *, started, minutes=None,
         result=None, progress=None, counts=None, code_requested=None):  # fmt: skip
    downloaded, present, failed = counts or (None, None, None)
    finished = started + timedelta(minutes=minutes) if minutes is not None else None
    session.add(CloudBackupRun(
        id=uuid.uuid4(), target_id=account.target_id, account_id=account.id,
        host_id=storage.id, action=action, status=status,
        queued_at=started - timedelta(seconds=15), started_at=started, finished_at=finished,
        requested_by="system" if action == "download" else AUTHOR,
        progress=json.dumps(progress) if progress else None,
        result=json.dumps(result) if result else None,
        exit_code=None if finished is None else (0 if status == "ok" else 1),
        downloaded=downloaded, present=present, failed_count=failed,
        password_released_at=started, code_requested_at=code_requested,
    ))  # fmt: skip


def _history(session, account, storage, state, last_good):
    """The account's last finished download, and a job running now."""
    if state in ("ok", "running") and last_good is not None:
        good = NOW - timedelta(hours=last_good)
        _run(session, account, storage, "download", "ok", started=good - timedelta(minutes=9),
             minutes=9, result={"reason": None, "duration": 540}, counts=(37, account.photos_local - 37, 0))  # fmt: skip
    if state == "running":
        _run(session, account, storage, "download", "running", started=NOW - timedelta(minutes=18),
             progress={"downloaded": 214, "at": NOW.isoformat()})  # fmt: skip
    elif state == "needs_sign_in":
        _run(session, account, storage, "download", "needs_sign_in", started=NOW - timedelta(hours=2),
             minutes=1, result={"reason": "session_expired"})  # fmt: skip
    elif state == "failed":
        _run(session, account, storage, "download", "failed", started=NOW - timedelta(hours=3),
             minutes=1, result={"reason": "web_access_off"})  # fmt: skip
    elif state == "waiting_code":
        _run(session, account, storage, "connect", "waiting_code", started=NOW - timedelta(minutes=2),
             code_requested=NOW - timedelta(minutes=1))  # fmt: skip


def _accounts(session, target, storage):
    for index, (name, apple_id, state, signed_in, last_good, photos, stored, auto_delete) \
            in enumerate(ACCOUNTS):  # fmt: skip
        account_id = uuid.uuid4()
        account = CloudBackupAccount(
            id=account_id, target_id=target.id, provider="icloud", apple_id=apple_id,
            display_name=name, library="PrimarySync", libraries=json.dumps(["PrimarySync"]),
            password_ref=f"secret/data/sysmanage/cloud-backup/{account_id}",
            password_set_at=NOW - timedelta(days=30 - index),
            dir_name="icloud-" + account_id.hex[:8], enabled=True, interval_hours=24,
            until_found=50, auto_delete=auto_delete,
            state="needs_sign_in" if state == "needs_sign_in" else
                  ("failed" if state == "failed" else ("new" if signed_in is None else "ok")),
            session_created_at=NOW - timedelta(days=signed_in) if signed_in is not None else None,
            last_good_at=NOW - timedelta(hours=last_good) if last_good is not None else None,
            last_full_at=NOW - timedelta(days=4) if last_good is not None else None,
            photos_local=photos, bytes_local=int(stored * GB) if stored else None,
            created_by=AUTHOR, created_at=NOW - timedelta(days=30 - index),
            updated_at=NOW - timedelta(hours=1),
        )  # fmt: skip
        session.add(account)
        session.flush()
        _history(session, account, storage, state, last_good)


def main() -> None:
    session = sessionmaker(bind=db.get_engine())()
    try:
        _clear(session)
        target = session.query(BackupTarget).first()
        storage = target and session.query(Host).filter(Host.id == target.storage_host_id).first()
        if storage is None:
            print("  no backup target with a storage host -- run seed_backups.py first")
            session.commit()
            return
        if ALT:
            session.commit()
            print("  iCloud backup left NOT enabled (alternate state)")
            return
        _enable(session, target, storage)
        _accounts(session, target, storage)
        session.commit()
        print(f"  + iCloud backup enabled on {storage.fqdn} (icloudpd {ICLOUDPD}), "
              f"{len(ACCOUNTS)} accounts: up to date, running, waiting for a code, "
              f"needs sign-in, failed")
    finally:
        session.close()


if __name__ == "__main__":
    main()
