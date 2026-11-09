#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Gate: no ROADMAP phase numbers in the published site.

Phases are SysManage's internal planning term (Bryan, 2026-11-05): "Phase 34",
"ROADMAP 27.3" and "roadmap Phase 25.9" mean nothing to a reader, and the
numbers go stale with every renumber -- six so far.  On 2026-11-09 they sat in
67 strings on 22 pages.  A page names the feature or the release instead
("planned", "since v2.2.0.0").

What is checked: every published page's text and its attribute values (a
<meta> description, a title), and every locale value of a key a page
references -- a reader sees the locale value, not the page's English.  File
names such as ``phase8-features.html`` are URLs, not prose, and are left
alone: the pattern needs a space (or &nbsp;) before the number.

    python3 scripts/check_no_phases.py
"""

import html
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LOCALES = REPO / "assets" / "locales"
SKIP_DIRS = {"node_modules", ".git", "SignPath", "Presentations", "screenshots", "__pycache__"}
PHASE = re.compile(r"\b(?:phases?|roadmap)(?:\s|&nbsp;| )+\d", re.IGNORECASE)
KEY = re.compile(r'data-i18n="([^"]+)"')


def pages():
    for path in sorted(REPO.rglob("*.html")):
        if not SKIP_DIRS.intersection(path.relative_to(REPO).parts):
            yield path


def flatten(node, prefix=""):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from flatten(value, f"{prefix}.{key}" if prefix else key)
    elif isinstance(node, str):
        yield prefix, node


def check():
    found, keys = [], set()
    for path in pages():
        text = path.read_text(encoding="utf-8")
        keys.update(KEY.findall(text))
        for number, line in enumerate(text.splitlines(), 1):
            if PHASE.search(html.unescape(line)):
                found.append(f"{path.relative_to(REPO)}:{number}")
    for path in sorted(LOCALES.glob("*.json")):
        if path.name.startswith(".") or path.stem == "missing_keys_analysis":
            continue
        for key, value in flatten(json.loads(path.read_text(encoding="utf-8"))):
            if key in keys and PHASE.search(html.unescape(value)):
                found.append(f"{path.relative_to(REPO)}: {key}")
    return found


def main() -> int:
    found = check()
    if not found:
        print("OK: no ROADMAP phase numbers in the published pages")
        return 0
    print(f"FAIL: {len(found)} place(s) cite a ROADMAP phase number:")
    for where in found:
        print(f"  {where}")
    print("Phases are an internal planning term. Name the feature, or the release")
    print('that shipped it ("planned", "since v2.2.0.0"), and update en.json too.')
    return 1


if __name__ == "__main__":
    sys.exit(main())
