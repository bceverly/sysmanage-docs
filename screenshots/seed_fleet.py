#!/usr/bin/env python3
"""Seed fleet_engine demo data (groups + a bulk op + a rolling deployment) via the
Pro+ fleet API so the host-detail Fleet tab isn't empty in the screenshots.

Why REST and not SQL: ``fleet_engine`` owns its storage internally — there is no ORM
model and no migration in the source tree (the schema is compiled into the engine),
so gen_seed_sql.py / seed_ent.py CANNOT touch it. The only safe way to populate it is
to POST through the engine's own validated endpoints (``/api/v1/fleet/*``).

Runs from the host against the licensed Enterprise VM (after ent-build / ent-seed).
DEFENSIVE BY DESIGN: every call is wrapped; an unlicensed engine (HTTP 402), an
endpoint-shape drift, or a network error is logged and skipped. This script never
exits non-zero, so it can never break the screenshot pipeline — worst case the Fleet
tab stays as it was.

Membership is pinned with ``explicit_host_ids`` (read from host_ids.json, written by
seed.py) so the target host is in the group regardless of how the UI computes it.
"""
from __future__ import annotations

import json
import os

# Reuse seed.py's request + login helpers (same dir → same /api base + auth). Importing
# is side-effect-free: seed.py guards its own run behind ``if __name__ == "__main__"``.
from seed import _req, login

HERE = os.path.dirname(__file__)
DOMAIN = "corp.northstar.io"


def _host_ids() -> dict:
    try:
        with open(os.path.join(HERE, "host_ids.json"), encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:  # noqa: BLE001 — optional; absence just means no explicit ids
        return {}


def _post(path: str, token: str, body: dict, label: str) -> None:
    try:
        status, _ = _req("POST", path, token=token, body=body)
    except Exception as exc:  # noqa: BLE001 — network/connection; never fatal
        print(f"  - skip {label}: {exc}")
        return
    if status in (200, 201):
        print(f"  + {label}")
    elif status == 402:
        print(f"  - skip {label}: fleet_engine not licensed (402)")
    else:
        print(f"  - skip {label}: HTTP {status}")


def main() -> int:
    ids = _host_ids()

    def hid(short: str):
        return ids.get(f"{short}.{DOMAIN}")

    web, db, app_, win = (
        hid("ubuntu-web-01"), hid("rhel-db-01"),
        hid("debian-app-01"), hid("win11-ws-01"),
    )
    prod_ids = [x for x in (web, db, win) if x]
    web_ids = [x for x in (web, app_) if x]

    try:
        token = login()
    except SystemExit as exc:
        print(f"  fleet seed skipped (no admin credentials): {exc}")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"  fleet seed skipped: {exc}")
        return 0

    print("Seeding fleet (groups / bulk / rolling) via /api/v1/fleet ...")

    # Groups — ubuntu-web-01 (the Fleet-tab screenshot host) is in BOTH so its tab fills.
    _post("/v1/fleet/groups", token, {
        "name": "Production Linux",
        "description": "All production Linux servers.",
        "explicit_host_ids": prod_ids, "tags": ["production"], "criteria": [],
    }, "group: Production Linux")
    _post("/v1/fleet/groups", token, {
        "name": "Web Tier",
        "description": "Front-end web / application hosts.",
        "explicit_host_ids": web_ids, "tags": ["web"], "criteria": [],
    }, "group: Web Tier")

    # A recent bulk operation + rolling deployment for the activity panes.
    _post("/v1/fleet/bulk", token, {
        "operation_type": "run_script",
        "selector": {"explicit_host_ids": prod_ids, "tags": ["production"]},
        "parameters": {"script_name": "Pending Reboot Check"},
        "description": "Pending-reboot sweep across production",
    }, "bulk: Pending-reboot sweep")
    _post("/v1/fleet/rolling", token, {
        "name": "Nginx config rollout",
        "operation_type": "run_script",
        "selector": {"explicit_host_ids": web_ids, "tags": ["web"]},
        "parameters": {"script_name": "Restart Nginx"},
        "batch_size": 1, "batch_delay_seconds": 30, "failure_threshold_pct": 10,
    }, "rolling: Nginx config rollout")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
