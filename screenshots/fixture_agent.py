#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""WebSocket fixture-agent for the documentation screenshots.

OS/platform/hardware inventory has no REST ingestion path in SysManage — it only
arrives through the agent's WebSocket protocol (``handle_system_info`` /
``os_version_update``). This script impersonates that protocol just enough to give
each seeded demo host a realistic OS so the dashboard OS-distribution tile and any
platform columns render correctly. It sends ONE ``os_version_update`` per host from
``fixtures.json`` and disconnects.

Run AFTER seed.py (the hosts must already be registered + approved). The agent WS
is a TWO-STAGE handshake, mirrored here per host:

  1. POST {target}/api/agent/auth  with header  x-agent-hostname: <fqdn>
       -> {"connection_token": "...", "expires_in": 3600, ...}
     (matches the real agent's build_auth_url(): .../api/agent/auth)
  2. ws(s)://<target>/api/agent/connect?token=<connection_token>
     The server reads the hostname from the (signed) token and sets it on the
     connection. handle_os_version_update then finds the host by
     ``Host.fqdn == connection.hostname`` — so the token's x-agent-hostname MUST
     be the host's FQDN. The hostname in the message data is not used for lookup.

  Envelope:     {"message_type","message_id","timestamp","data"}  (messages.py to_dict)
  Message type: "os_version_update"  (MessageType.OS_VERSION_UPDATE)

Everything upstream (REST seed) and downstream (capture) is independent of this.

Usage:
    SCREENSHOT_TARGET=http://localhost:8080 python3 fixture_agent.py
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone

try:
    import websockets
except ImportError:
    sys.exit("ERROR: pip install websockets")

TARGET = os.environ.get("SCREENSHOT_TARGET", "http://localhost:8080").rstrip("/")
AUTH_URL = TARGET + "/api/agent/auth"  # matches the real agent's build_auth_url()
WS_BASE = TARGET.replace("https://", "wss://").replace("http://", "ws://") + "/api/agent/connect"


def get_connection_token(fqdn: str) -> str:
    """Stage 1: obtain a signed connection token bound to this host's FQDN."""
    req = urllib.request.Request(
        AUTH_URL, data=b"", method="POST",
        headers={"x-agent-hostname": fqdn, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:  # nosec B310 - operator-supplied target
        body = json.loads(resp.read().decode() or "{}")
    token = body.get("connection_token")
    if not token:
        raise RuntimeError(f"no connection_token in /agent/auth response: {body}")
    return token


def _envelope(message_type: str, data: dict) -> dict:
    """Wrap a payload in the standard agent message envelope (messages.py to_dict)."""
    return {
        "message_type": message_type,
        "message_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }


def messages_for(host: dict) -> list[dict]:
    """Build the OS-version message we report for one host.

    Only OS/platform is reported over the WebSocket (this is the path that reliably
    persists for the dashboard OS-distribution tile). Hardware/storage/network/
    software inventory is seeded directly by seed_inventory.sql, OS-upgrade
    candidates by the REST updates report (seed.py), and map coordinates +
    last_access by seed_geo.sql — those WS handlers depend on a queue-worker
    host association that isn't reliable from a throwaway fixture.
    """
    return [
        _envelope("os_version_update", {
            "hostname": host["hostname"], "fqdn": host["fqdn"],
            "platform": host.get("platform"),
            "platform_release": host.get("platform_release"),
            "platform_version": host.get("platform_version"),
            "architecture": host.get("architecture"),
            "machine_architecture": host.get("architecture"),
            "processor": host.get("architecture"),
            "python_version": "3.12.0",
            "os_info": {
                "system": host.get("platform"), "release": host.get("platform_release"),
                "version": host.get("platform_version"), "machine": host.get("architecture"),
            },
        }),
    ]


async def report_host(host: dict) -> bool:
    try:
        token = get_connection_token(host["fqdn"])  # stage 1 (sync REST)
        ws_url = f"{WS_BASE}?token={token}"
        async with websockets.connect(ws_url, open_timeout=15, close_timeout=5) as ws:
            for msg in messages_for(host):
                await ws.send(json.dumps(msg))
                # Drain the ack briefly so messages are processed in order.
                try:
                    await asyncio.wait_for(ws.recv(), timeout=2)
                except (asyncio.TimeoutError, Exception):  # noqa: BLE001 - best-effort drain
                    pass
        print(f"  reported OS+inventory for {host['fqdn']} ({host.get('platform_version')})")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"  WARN could not report {host['fqdn']}: {exc}", file=sys.stderr)
        return False


async def main() -> int:
    here = os.path.dirname(__file__)
    data = json.load(open(os.path.join(here, "fixtures.json"), encoding="utf-8"))
    print(f"Reporting OS/inventory to {WS_BASE} ...")
    ok = 0
    for host in data["hosts"]:
        if await report_host(host):
            ok += 1
    print(f"\nReported {ok}/{len(data['hosts'])} hosts.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
