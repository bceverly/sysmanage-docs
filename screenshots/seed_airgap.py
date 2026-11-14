#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Seed an air-gap disc SET for the air-gap screenshots (Enterprise VM).

Runs INSIDE the screenshot VM against the sysmanage ORM, like the other
seeders.  Apply via:  make screenshots-airgap-seed  (after
screenshots-ent-seed, which makes the mirrors and the single-disc run this
builds on; seed_ent.py is at the 1000-line ceiling, so this lives apart).

WHAT IT HAS TO SHOW, AND WHY
----------------------------
  * The collector side: a COMPLETE run that was larger than its Media Size
    (4700 MB, a single-layer DVD) and so was split into a set of three
    discs, one whole mirror each, the SysManage tools on disc 1.  Its
    Download asks which disc to fetch (the disc picker), and the picker
    reads the disc files themselves (``GET /runs/{id}/discs`` lists
    ``<run>-disc-N.iso`` in /var/lib/sysmanage/airgap-iso and reports their
    sizes), so the three files are written here -- SPARSE, a few kilobytes
    on the VM's disk for the gigabytes they report.
  * The repository side, a set imported disc by disc: disc 1 imported
    (the latest import, COMPLETE, with its file count and size) and disc 2
    in the import drive, ready.  The drive is probed live with lsblk (an
    iso9660 filesystem is what makes it ready), so disc 2 is a real ISO:
    a small one made with xorriso, attached read-only to a loop device,
    and that device chosen as the import drive.  The loop device lasts
    until the VM reboots; re-run this seed after one.

Idempotent: clears its own run, manifests, ingest rows and disc files, and
detaches its earlier loop device, first.
"""

import glob
import json
import os
import shutil
# Fixed argv only: xorriso, losetup, udevadm, apt-get.
import subprocess  # nosec B404
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from backend.persistence import db
from backend.persistence.models import MirrorRepository, ServerConfiguration, User
from backend.persistence.models.airgap import (
    AirgapCollectionRun,
    AirgapCollectionTarget,
    AirgapIngestionRun,
    AirgapMediaManifest,
)

NOW = datetime.now(timezone.utc).replace(tzinfo=None)
LABEL = "airgap-2026-11-full"
MEDIA = 4_700_000_000
BURN_DEVICE = "/dev/sr0"
ISO_DIR = "/var/lib/sysmanage/airgap-iso"
FINGERPRINT = "3f9c2a7e" * 8
# One whole mirror per disc; the tools ride on disc 1.  (distro, version,
# repos, package manager of the mirror to point at, bytes, files)
DISCS = [
    ("ubuntu", "22.04", "main,security", "apt", 4_052_000_000, 61_240),
    ("rocky", "9", "BaseOS,AppStream", "dnf", 4_410_000_000, 9_100),
    ("freebsd", "14", "latest", "pkg", 2_031_000_000, 33_500),
]
# Disc 2 as it sits in the import drive (the ISO volume label lsblk reads).
DISC2_VOLUME = "AIRGAP_2026_11_FULL_2"
WORK = os.path.join(os.path.expanduser("~"), ".cache", "sysmanage-shots", "airgap")
DISC2_ISO = os.path.join(WORK, "disc-2.iso")


def _run(argv, check=True):
    return subprocess.run(argv, capture_output=True, text=True, check=check, timeout=600)  # nosec B603


def _private_dir():
    os.makedirs(WORK, mode=0o700, exist_ok=True)
    if os.path.islink(WORK) or not os.path.isdir(WORK):
        raise SystemExit(f"{WORK} is not a real directory; remove it and re-run")
    os.chmod(WORK, 0o700)


def _clear(session):
    old = session.query(AirgapCollectionRun).filter(AirgapCollectionRun.iso_label == LABEL).all()
    for run in old:
        for path in glob.glob(os.path.join(ISO_DIR, f"{run.id}-disc-*.iso")):
            os.remove(path)
        session.query(AirgapMediaManifest).filter(AirgapMediaManifest.run_id == run.id).delete()
        session.query(AirgapCollectionTarget).filter(AirgapCollectionTarget.run_id == run.id).delete()
        session.delete(run)
    session.query(AirgapIngestionRun).filter(
        AirgapIngestionRun.collector_iso_label == LABEL
    ).delete()
    session.flush()


def _mirror(session, manager):
    """A mirror seed_ent.py made (the runs API 500s on an empty mirror_id)."""
    found = session.query(MirrorRepository).filter(MirrorRepository.package_manager == manager).first()
    return found or session.query(MirrorRepository).first()


def _collection_set(session):
    admin = session.query(User).filter(User.userid == "admin@sysmanage.org").first()
    run = AirgapCollectionRun(
        id=uuid.uuid4(), iso_label=LABEL, media_size_bytes=MEDIA,
        include_cve=True, include_compliance=True, status="COMPLETE",
        burn_device=BURN_DEVICE,
        started_at=NOW - timedelta(hours=2, minutes=10),
        completed_at=NOW - timedelta(minutes=55),
        created_at=NOW - timedelta(hours=2, minutes=10),
        created_by=admin.id if admin else None,
    )  # fmt: skip
    session.add(run)
    session.flush()
    os.makedirs(ISO_DIR, mode=0o755, exist_ok=True)
    count = len(DISCS)
    for index, (distro, version, repos, manager, size, files) in enumerate(DISCS, start=1):
        mirror = _mirror(session, manager)
        session.add(AirgapCollectionTarget(
            run_id=run.id, distro=distro, version=version, repos=repos,
            byte_count=size, file_count=files, status="COMPLETE",
            mirror_id=mirror.id if mirror else None,
        ))  # fmt: skip
        path = os.path.join(ISO_DIR, f"{run.id}-disc-{index}.iso")
        with open(path, "wb") as handle:
            handle.truncate(size)  # sparse: the size is what the picker shows
        session.add(AirgapMediaManifest(
            run_id=run.id, disc_index=index, disc_count=count, iso_path=path,
            iso_sha256=f"{index:x}" * 64, iso_size_bytes=size,
            manifest_json=json.dumps({"disc": index, "discs": count,
                                      "targets": [f"{distro}:{version}"],
                                      "tools": index == 1}),  # fmt: skip
            signature="demo-signature", signer_fingerprint=FINGERPRINT,
            created_at=NOW - timedelta(minutes=55),
        ))  # fmt: skip
    return run


def _disc1_imported(session, device):
    """The latest import: disc 1 of the set, COMPLETE."""
    distro, version, _repos, _manager, size, files = DISCS[0]
    session.add(AirgapIngestionRun(
        iso_path=device, iso_sha256="1" * 64, signer_fingerprint=FINGERPRINT,
        manifest_format_version=1, collector_iso_label=LABEL,
        captured_at=NOW - timedelta(hours=2, minutes=10), status="COMPLETE",
        started_at=NOW - timedelta(minutes=24), completed_at=NOW - timedelta(minutes=9),
        file_count=files, byte_count=size, created_at=NOW - timedelta(minutes=24),
    ))  # fmt: skip
    print(f"  + ingest: disc 1 ({distro} {version}) imported, {files} files")


def _xorriso():
    if shutil.which("xorriso"):
        return shutil.which("xorriso")
    print("  installing xorriso (the import drive needs a real ISO)...")
    _run(["apt-get", "-o", "DPkg::Lock::Timeout=600", "install", "-y", "-q", "xorriso"])
    return shutil.which("xorriso")


def _detach_earlier():
    if not os.path.exists(DISC2_ISO):
        return
    out = _run(["losetup", "-j", DISC2_ISO], check=False).stdout
    for line in out.splitlines():
        device = line.split(":", 1)[0].strip()
        if device.startswith("/dev/loop"):
            _run(["losetup", "-d", device], check=False)


def _disc2_in_drive():
    """Disc 2 as a real, read-only ISO on a loop device; its path, or None."""
    _private_dir()
    _detach_earlier()
    xorriso = _xorriso()
    if not xorriso:
        print("  note: no xorriso; the import drive is left unselected")
        return None
    tree = os.path.join(WORK, "disc-2")
    os.makedirs(tree, exist_ok=True)
    with open(os.path.join(tree, "README.txt"), "w", encoding="utf-8") as handle:
        handle.write(f"{LABEL} disc 2 of {len(DISCS)} (screenshot fixture)\n")
    _run([xorriso, "-as", "mkisofs", "-V", DISC2_VOLUME, "-o", DISC2_ISO, tree])
    device = _run(["losetup", "--find", "--show", "--read-only", DISC2_ISO]).stdout.strip()
    _run(["udevadm", "settle"], check=False)
    return device or None


def main() -> None:
    session = sessionmaker(bind=db.get_engine())()
    try:
        _clear(session)
        run = _collection_set(session)
        device = _disc2_in_drive()
        _disc1_imported(session, device or BURN_DEVICE)
        cfg = session.query(ServerConfiguration).first()
        if cfg is not None and device:
            cfg.airgap_import_device = device
        session.commit()
        print(f"  + air-gap set: run {run.id}, {len(DISCS)} discs ({MEDIA // 1_000_000} MB each at most)")
        if device:
            # pylint: disable-next=import-outside-toplevel
            from backend.services import airgap_device_service

            status = airgap_device_service.probe_device(device)
            print(f"  + import drive {device}: ready={status.get('ready')} "
                  f"label={status.get('label')} ({status.get('reason')})")  # fmt: skip
    finally:
        session.close()


if __name__ == "__main__":
    main()
