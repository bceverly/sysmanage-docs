#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""REST seeder for the SysManage documentation screenshots.

Injects the deterministic demo data from ``fixtures.json`` into a *running*
SysManage instance through the REST API only — host records, available updates,
tags + assignments, and users. Per-host OS/inventory (which has no REST ingestion
path) is reported separately by ``fixture_agent.py`` over the agent WebSocket.

This script is environment-agnostic: point it at the Vagrant VM, or at any dev
instance, via ``SCREENSHOT_TARGET`` (default http://localhost:8080). That lets you
iterate on seeding/capture without rebuilding the VM.

Grounded in the live API:
  POST /login                          -> JWT (UserLogin: userid, password)
  POST /host/register                  -> create host (minimal: fqdn/hostname/ipv4)
  PUT  /host/{id}/approve              -> approve
  POST /updates/report/{host_id}       -> available updates (UpdatesReport)
  POST /tags  /  POST /hosts/{id}/tags/{tag_id}
  POST /user

Idempotency: re-running is safe-ish — it tolerates "already exists" responses and
matches existing hosts/tags/users by their natural keys.

Usage:
    SCREENSHOT_TARGET=http://localhost:8080 \
    SCREENSHOT_ADMIN=admin@sysmanage.org SCREENSHOT_ADMIN_PW=... \
    python3 seed.py [--fixtures fixtures.json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

TARGET = os.environ.get("SCREENSHOT_TARGET", "http://localhost:8080").rstrip("/")
ADMIN = os.environ.get("SCREENSHOT_ADMIN", "admin@sysmanage.org")
ADMIN_PW = os.environ.get("SCREENSHOT_ADMIN_PW", "")


class ApiError(Exception):
    pass


def _req_once(method: str, url: str, token: str | None, body: dict | None) -> tuple[int, dict]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        # B310 rationale: operator-supplied target (trusted screenshot VM), http(s) only.
        with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310
            raw = resp.read().decode() or "{}"
            return resp.status, (json.loads(raw) if raw.strip().startswith(("{", "[")) else {"_raw": raw})
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, {"_raw": raw}
    except urllib.error.URLError as exc:
        raise ApiError(f"cannot reach {url}: {exc}") from exc


def _req(method: str, path: str, token: str | None = None, body: dict | None = None) -> tuple[int, dict]:
    # Native OSS feature routes moved under /api/v1 (the /api bridge was retired);
    # a few surfaces (agent, auth/mfa, SCIM, certificates) stay bare /api.  Try the
    # versioned path first and fall back to bare /api so this works across both.
    # Fall back on 404 AND 405: a bare-/api-only endpoint (e.g. the agent-facing
    # POST /host/register) can collide with a DIFFERENT-method /api/v1 route at the
    # same path, which returns 405 (Method Not Allowed) rather than 404.
    if path.startswith("/v1/"):
        return _req_once(method, f"{TARGET}/api{path}", token, body)
    status, resp = _req_once(method, f"{TARGET}/api/v1{path}", token, body)
    if status in (404, 405):
        return _req_once(method, f"{TARGET}/api{path}", token, body)
    return status, resp


def login() -> str:
    if not ADMIN_PW:
        sys.exit("ERROR: set SCREENSHOT_ADMIN_PW (the admin password from the VM's "
                 "sysmanage.yaml / secure installer).")
    status, body = _req("POST", "/login", body={"userid": ADMIN, "password": ADMIN_PW})
    if status != 200:
        sys.exit(f"ERROR: login failed ({status}): {body}")
    # The login endpoint returns an access token (body and/or cookie). Accept the
    # common field names; fall back to a cookie-less bearer if present.
    token = body.get("access_token") or body.get("token") or body.get("Authorization")
    if not token:
        sys.exit(f"ERROR: login succeeded but no access_token in response: {list(body)}")
    return token.replace("Bearer ", "")


def register_and_approve_hosts(token: str, hosts: list[dict]) -> dict[str, str]:
    """Return {fqdn: host_id} for every host (created or pre-existing)."""
    fqdn_to_id: dict[str, str] = {}
    # Map of existing hosts so re-runs find ids.
    _, existing = _req("GET", "/hosts", token=token)
    if isinstance(existing, list):
        for h in existing:
            if h.get("fqdn"):
                fqdn_to_id[h["fqdn"]] = str(h.get("id"))

    for h in hosts:
        if h["fqdn"] in fqdn_to_id:
            print(f"  host exists: {h['fqdn']}")
            continue
        status, body = _req("POST", "/host/register", body={
            "active": True, "fqdn": h["fqdn"], "hostname": h["hostname"],
            "ipv4": h.get("ipv4"), "agent_version": "1.4.0",
        })
        if status not in (200, 201):
            print(f"  WARN register {h['fqdn']} -> {status}: {body}", file=sys.stderr)
            continue
        host_id = str(body.get("id") or body.get("host_id") or "")
        if not host_id:
            # Re-read the host list to find the new id by fqdn.
            _, lst = _req("GET", "/hosts", token=token)
            host_id = next((str(x["id"]) for x in (lst or []) if x.get("fqdn") == h["fqdn"]), "")
        if host_id:
            fqdn_to_id[h["fqdn"]] = host_id
            # A host with "approve": false stays pending — it demonstrates the
            # agent-approval queue on the Hosts page.
            if h.get("approve", True) is False:
                print(f"  registered (PENDING approval): {h['fqdn']} ({host_id})")
                continue
            _req("PUT", f"/host/{host_id}/approve", token=token)
            print(f"  registered + approved: {h['fqdn']} ({host_id})")
        else:
            print(f"  WARN could not resolve host_id for {h['fqdn']}", file=sys.stderr)
    return fqdn_to_id


def seed_updates(token: str, hosts: list[dict], fqdn_to_id: dict[str, str]) -> None:
    for h in hosts:
        host_id = fqdn_to_id.get(h["fqdn"])
        if not host_id:
            continue
        u = h.get("updates", {})
        avail = []
        for i in range(u.get("security", 0)):
            avail.append(_pkg(f"sec-pkg-{i}", h, security=True))
        for i in range(u.get("system", 0)):
            avail.append(_pkg(f"sys-pkg-{i}", h, system=True))
        for i in range(u.get("application", 0)):
            avail.append(_pkg(f"app-pkg-{i}", h))
        # OS-upgrade candidate -> /os-upgrades page. Goes through the same REST
        # updates report as regular updates; what makes it an OS upgrade is the
        # OS-release package_manager (ubuntu-release/freebsd-upgrade/...).
        up_os = h.get("os_upgrade")
        if up_os:
            avail.append({
                "package_name": up_os["package_name"],
                "current_version": up_os.get("current_version"),
                "available_version": up_os.get("new_version"),
                "package_manager": up_os["package_manager"],
                "is_security_update": False, "is_system_update": False,
                "requires_reboot": up_os.get("requires_reboot", True),
                "update_size_bytes": up_os.get("update_size", 0),
            })
        report = {
            "available_updates": avail,
            "total_updates": len(avail),
            "security_updates": u.get("security", 0),
            "system_updates": u.get("system", 0),
            "application_updates": u.get("application", 0),
            "platform": h.get("platform", "Linux"),
            "requires_reboot": u.get("requires_reboot", False),
        }
        status, body = _req("POST", f"/updates/report/{host_id}", token=token, body=report)
        if status in (200, 201):
            print(f"  updates seeded: {h['fqdn']} ({len(avail)})")
        else:
            print(f"  WARN updates {h['fqdn']} -> {status}: {body}", file=sys.stderr)


def _pkg(name: str, h: dict, security=False, system=False) -> dict:
    pm = {"Linux": "apt", "FreeBSD": "pkg", "Windows": "winget", "Darwin": "brew"}.get(h.get("platform"), "apt")
    return {
        "package_name": name, "current_version": "1.0.0", "available_version": "1.0.1",
        "package_manager": pm, "is_security_update": security, "is_system_update": system,
        "requires_reboot": False, "update_size_bytes": 1048576,
    }


def seed_tags(token: str, tags: list[dict], hosts: list[dict], fqdn_to_id: dict[str, str]) -> None:
    name_to_id: dict[str, str] = {}
    _, existing = _req("GET", "/tags", token=token)
    if isinstance(existing, list):
        for t in existing:
            name_to_id[t.get("name")] = str(t.get("id"))
    for t in tags:
        if t["name"] in name_to_id:
            continue
        status, body = _req("POST", "/tags", token=token, body={"name": t["name"], "description": t.get("description")})
        if status in (200, 201):
            name_to_id[t["name"]] = str(body.get("id"))
            print(f"  tag created: {t['name']}")
    for h in hosts:
        host_id = fqdn_to_id.get(h["fqdn"])
        for tag_name in h.get("tags", []):
            tag_id = name_to_id.get(tag_name)
            if host_id and tag_id:
                _req("POST", f"/hosts/{host_id}/tags/{tag_id}", token=token)
    print("  tag assignments done")


def seed_scripts(token: str, scripts: list[dict], fqdn_to_id: dict[str, str]) -> None:
    """Create the saved-script library, and queue one execution per script that
    declares a `run_on` host (populates the Scripts > Execution history tab)."""
    name_to_id: dict[str, str] = {}
    _, existing = _req("GET", "/scripts/", token=token)
    rows = existing if isinstance(existing, list) else existing.get("scripts", []) if isinstance(existing, dict) else []
    for s in rows or []:
        if s.get("name"):
            name_to_id[s["name"]] = str(s.get("id"))
    for s in scripts:
        if s["name"] in name_to_id:
            print(f"  script exists: {s['name']}")
            continue
        status, body = _req("POST", "/scripts/", token=token, body={
            "name": s["name"], "description": s.get("description"), "content": s["content"],
            "shell_type": s.get("shell_type", "bash"), "platform": s.get("platform", "linux"),
            "run_as_user": s.get("run_as_user"),
        })
        if status in (200, 201):
            name_to_id[s["name"]] = str(body.get("id"))
            print(f"  script created: {s['name']}")
        else:
            print(f"  WARN script {s['name']} -> {status}: {body}", file=sys.stderr)
    # Queue one execution per script targeting a real host, for the history tab.
    for s in scripts:
        host_id = fqdn_to_id.get(s.get("run_on", ""))
        if not host_id:
            continue
        status, body = _req("POST", "/scripts/execute", token=token, body={
            "host_id": host_id, "saved_script_id": name_to_id.get(s["name"]),
            "script_content": s["content"], "shell_type": s.get("shell_type", "bash"),
            "script_name": s["name"], "run_as_user": s.get("run_as_user"),
        })
        if status in (200, 201):
            print(f"  script execution queued: {s['name']} -> {s['run_on']}")
        else:
            print(f"  WARN execute {s['name']} -> {status}: {body}", file=sys.stderr)


def seed_users(token: str, users: list[dict]) -> None:
    for u in users:
        status, body = _req("POST", "/user", token=token, body={
            "userid": u["userid"], "password": u.get("password"),
            "first_name": u.get("first_name"), "last_name": u.get("last_name"),
            "active": True,
        })
        if status in (200, 201):
            print(f"  user created: {u['userid']}")
        elif status in (400, 409):
            print(f"  user exists: {u['userid']}")
        else:
            print(f"  WARN user {u['userid']} -> {status}: {body}", file=sys.stderr)


def seed_maintenance_windows(token: str, fqdn_to_id: dict[str, str]) -> None:
    """Create a few demo maintenance windows (Phase 14.2) so the Maintenance
    Windows page + host card have content for screenshots.  Idempotent by name.
    Posts to the native /api/v1/maintenance-windows route."""
    _, existing = _req("GET", "/v1/maintenance-windows", token=token)
    have = {
        w.get("name")
        for w in (existing.get("windows", []) if isinstance(existing, dict) else [])
    }
    windows = [
        {
            "name": "Nightly Patching",
            "description": "Routine patch installs run overnight.",
            "enabled": True,
            "kind": "allow",
            "recurrence": "daily",
            "timezone": "UTC",
            "start_time": "02:00",
            "duration_minutes": 120,
            "scopes": [{"scope_type": "all"}],
        },
        {
            "name": "Weekend Change Freeze",
            "description": "No automated changes over the weekend.",
            "enabled": True,
            "kind": "blackout",
            "recurrence": "weekly",
            "timezone": "UTC",
            "start_time": "00:00",
            "duration_minutes": 1440,
            "days_of_week": ["sat", "sun"],
            "scopes": [{"scope_type": "all"}],
        },
    ]
    # A host-scoped window for the database server, if that host exists.
    db_host = fqdn_to_id.get("rhel-db-01.corp.northstar.io")
    if db_host:
        windows.append(
            {
                "name": "Database Servers",
                "description": "Database maintenance, Sunday mornings (US Eastern).",
                "enabled": True,
                "kind": "allow",
                "recurrence": "weekly",
                "timezone": "America/New_York",
                "start_time": "03:00",
                "duration_minutes": 180,
                "days_of_week": ["sun"],
                "scopes": [{"scope_type": "host", "host_id": db_host}],
            }
        )
    for w in windows:
        if w["name"] in have:
            print(f"  maintenance window exists: {w['name']}")
            continue
        status, body = _req(
            "POST", "/v1/maintenance-windows", token=token, body=w
        )
        if status in (200, 201):
            print(f"  maintenance window created: {w['name']}")
        else:
            print(
                f"  WARN maintenance window {w['name']} -> {status}: {body}",
                file=sys.stderr,
            )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fixtures", default=os.path.join(os.path.dirname(__file__), "fixtures.json"))
    args = ap.parse_args()
    with open(args.fixtures, encoding="utf-8") as _fx:
        data = json.load(_fx)

    print(f"Seeding {TARGET} as {ADMIN} ...")
    token = login()
    print("Hosts:")
    fqdn_to_id = register_and_approve_hosts(token, data["hosts"])
    # Write the fqdn->id map so capture.mjs can deep-link to /hosts/<id> for the
    # host-detail shots (more robust than clicking a role-gated row icon).
    with open(os.path.join(os.path.dirname(__file__), "host_ids.json"), "w", encoding="utf-8") as fh:
        json.dump(fqdn_to_id, fh, indent=2)
    print("Updates:")
    seed_updates(token, data["hosts"], fqdn_to_id)
    print("Tags:")
    seed_tags(token, data["tags"], data["hosts"], fqdn_to_id)
    print("Users:")
    seed_users(token, data["users"])
    if data.get("scripts"):
        print("Scripts:")
        seed_scripts(token, data["scripts"], fqdn_to_id)
    print("Maintenance windows:")
    seed_maintenance_windows(token, fqdn_to_id)
    print("\nREST seed complete. Run fixture_agent.py next to report per-host OS/inventory.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
