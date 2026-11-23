#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""The version the docs home names must be the current release.

``docs/index.html`` says "These pages describe SysManage <strong>X.Y</strong>"
and said 3.12 well after 3.15 shipped (Bryan, 2026-11-23): nothing checked
it.  The current release is the one release-notes.html marks "(current)".
This fails when the docs home -- or any locale's copy of that sentence --
names another version, so it cannot drift again.

    python3 scripts/check_docs_version.py
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CURRENT = re.compile(r'data-i18n="docs\.releases\.h_\d+">(\d+\.\d+)\b[^<]*\(current\)')
HOME = re.compile(r'data-i18n="docs\.landing\.version"[^>]*>.*?<strong>(\d+\.\d+)</strong>', re.S)
NAMED = re.compile(r"<strong>\s*(\d+\.\d+)\s*</strong>")


def main() -> int:
    notes = (REPO / "docs" / "release-notes.html").read_text(encoding="utf-8")
    found = CURRENT.findall(notes)
    if len(found) != 1:
        print(f"FAIL: release-notes.html must mark exactly one release (current); found {found}")
        return 1
    current = found[0]
    problems = []
    home = HOME.search((REPO / "docs" / "index.html").read_text(encoding="utf-8"))
    if not home or home.group(1) != current:
        problems.append(f"docs/index.html names {home.group(1) if home else 'no version'}")
    for path in sorted((REPO / "assets" / "locales").glob("[!.]*.json")):
        value = json.loads(path.read_text(encoding="utf-8")).get("docs", {}).get(
            "landing", {}).get("version", "")
        named = NAMED.findall(value)
        if named != [current]:
            problems.append(f"{path.name} docs.landing.version names {named or 'no version'}")
    if problems:
        print(f"FAIL: the docs home must describe the current release, {current}:")
        for line in problems:
            print("  " + line)
        print("Fix: change the <strong>X.Y</strong> in docs/index.html and in every")
        print("locale's docs.landing.version to the release marked (current).")
        return 1
    print(f"[OK] the docs home describes the current release ({current})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
