#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Seed machines and asset tags (Phase 23.2) -- through the REAL paths.

Runs INSIDE the screenshot VM against the sysmanage ORM, like the other
seeders.  Apply via:  make screenshots-assettag-seed

WHY IT SENDS IDENTITIES INSTEAD OF WRITING MACHINE ROWS
-------------------------------------------------------
Which hosts share a machine is a VERDICT the server makes from what agents
report.  This seeder hands each demo host the ``hardware_identity`` its agent
would send to ``machine_identity.record_identity`` -- the function the
hardware handler calls -- so every link, every "other operating systems on
this machine" row and the virtual-machine flag on screen is one the product
computed.  Tags go in through the real CSV import (``asset_tag_csv.apply``),
which is also what creates the pending tag.

WHAT IT HAS TO SHOW, AND WHY
----------------------------
  * A multi-boot workstation: win11-ws-01 and ubuntu-ws-07 (the newly
    registered host in the approval shots) are two OSes on ONE Dell, so both
    hardware tabs show the same machine and the same tag.
  * A virtual machine: debian-app-01 is QEMU, flagged virtual, left untagged.
  * A tag from before the scheme: freebsd-build-01 keeps "LEGACY-0042", which
    the Settings page reports as not conforming -- and never rewrites.
  * Untagged hardware: macos-studio-01 and the VM, for the Untagged Machines
    report.
  * A pending tag for a laptop that has not reported in yet.

Identities are SCRAMBLED (realistic shapes, invented digits).  Run AFTER
screenshots-seed (demo hosts).  Idempotent: clears machines, holds and the
scheme first.
"""

from sqlalchemy.orm import sessionmaker

from backend.persistence import db
from backend.persistence.models import AssetTagScheme, HeldAssetTag, Host, Machine, User
from backend.persistence.models.machine import ASSET_TAG_SCHEME_ID
from backend.services import asset_tag_csv, asset_tag_scheme, held_asset_tags
from backend.services import machine_identity

AUTHOR = "admin@sysmanage.org"
DOMAIN = "corp.northstar.io"

DELL_WS_UUID = "4c4c4544-0046-3310-8033-b9c04f4b4a54"
# fqdn -> (system UUID, system serial, board serial, vendor, model)
IDENTITIES = {
    "ubuntu-web-01": (
        "4c4c4544-0052-4b10-8037-c2c04f513533",
        "7XK2Q53",
        ".7XK2Q53.CNIVC0083F00LR.",
        "Dell Inc.",
        "PowerEdge R640",
    ),
    "rhel-db-01": (
        "37383638-3330-4d32-3231-3439304b5434",
        "MXQ12904KT",
        "PWAQA0CRHAB1QX",
        "HPE",
        "ProLiant DL380 Gen10",
    ),
    "debian-app-01": (
        "8b6f2a41-93c7-4e0d-b1a5-6d2e7f30c918",
        None,
        None,
        "QEMU",
        "Standard PC (Q35 + ICH9, 2009)",
    ),
    "freebsd-build-01": (
        "00000000-0000-0000-0000-ac1f6b4d27e0",
        "S437812X",
        "OM21AS031472",
        "Supermicro",
        "SYS-E300-12D",
    ),
    "win11-ws-01": (DELL_WS_UUID, "9F3KJT3", "/9F3KJT3/CNFCW0028M00G1/", "Dell Inc.", "Precision 3660"),
    "ubuntu-ws-07": (DELL_WS_UUID, "9F3KJT3", "/9F3KJT3/CNFCW0028M00G1/", "Dell Inc.", "Precision 3660"),
    "macos-studio-01": (
        "6a3f9d02-51be-4c7e-9e48-0b27c1d84f66",
        "C02XK0ABJGH5",
        None,
        "Apple Inc.",
        "Mac16,9",
    ),
}

SCHEME = asset_tag_scheme.Scheme(
    prefix="NST", separator="-", digits=5, suffix="", enforce=True
)

# The import the docs show: assigned by UUID or by serial, and one laptop that
# has not reported in yet (held).
IMPORT_CSV = (
    "system_uuid,system_serial,asset_tag\n"
    "4c4c4544-0052-4b10-8037-c2c04f513533,,NST-00101\n"
    ",MXQ12904KT,NST-00102\n"
    ",9F3KJT3,NST-00117\n"
    ",5CG2481KQZ,NST-00121\n"
)


def _identity(raw_uuid, serial, board, vendor, model):
    status = {
        "system_uuid": "ran",
        "system_serial": "ran" if serial else "absent",
        "board_serial": "ran" if board else "absent",
    }
    return {
        "system_uuid": raw_uuid,
        "system_serial": serial,
        "board_serial": board,
        "vendor": vendor,
        "model": model,
        "match_key": held_asset_tags.uuid_key(raw_uuid)[0],
        "status": status,
    }


def _clear(session) -> None:
    session.query(HeldAssetTag).delete()
    for host in session.query(Host).filter(Host.machine_id.isnot(None)).all():
        host.machine_id = None
    for host in session.query(Host).filter(Host.machine_conflict_id.isnot(None)).all():
        host.machine_conflict_id = None
        host.machine_conflict_reason = None
    session.query(Machine).delete()
    session.query(AssetTagScheme).delete()
    session.flush()


def main() -> None:
    session = sessionmaker(bind=db.get_engine())()
    try:
        _clear(session)
        linked = 0
        for name, parts in IDENTITIES.items():
            host = session.query(Host).filter(Host.fqdn == f"{name}.{DOMAIN}").first()
            if host is None:
                print(f"  - skip {name}: demo host not found (run screenshots-seed first)")
                continue
            machine_identity.record_identity(session, host, _identity(*parts))
            session.flush()
            linked += 1
        if not linked:
            # Same contract as the other seeders: no fleet, no data.  Going on
            # would import every CSV row as a PENDING tag for machines that
            # simply were not seeded -- a screenshot of the wrong state.
            session.rollback()
            print("  no demo hosts present -- run make screenshots-seed first")
            return
        print(f"  + {linked} hosts reported their hardware identity")

        # A tag from before anyone defined a scheme -- the scheme reports it.
        freebsd = (
            session.query(Host).filter(Host.fqdn == f"freebsd-build-01.{DOMAIN}").first()
        )
        if freebsd is not None and freebsd.machine_id:
            session.get(Machine, freebsd.machine_id).asset_tag = "LEGACY-0042"

        row = AssetTagScheme(id=ASSET_TAG_SCHEME_ID)
        for field in ("mode", "prefix", "separator", "digits", "suffix", "pattern", "enforce"):
            setattr(row, field, getattr(SCHEME, field))
        row.updated_by = AUTHOR
        session.add(row)
        session.flush()

        user = session.query(User).filter(User.userid == AUTHOR).first()
        rows = asset_tag_csv.apply(
            session, IMPORT_CSV, SCHEME, user.id if user else None, AUTHOR
        )
        session.commit()
        print(f"  + CSV import: {asset_tag_csv.summary(rows)}")
        print(f"  + {session.query(Machine).count()} machines, "
              f"{session.query(HeldAssetTag).count()} pending tag(s)")
    finally:
        session.close()


main()
