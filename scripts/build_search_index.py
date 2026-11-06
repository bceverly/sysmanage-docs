#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Build the documentation search index, one file per language.

The site is static, so search runs in the browser (assets/js/search.js)
against ``assets/search/<lang>.json``.  Each page's words come from the
locale store through the page's own ``data-i18n`` keys, so a German reader
searches the German text.  Generated at deploy time (deploy.yml) -- never
committed, so it cannot go stale -- and by ``make search-index`` locally.

Usage: build_search_index.py [site root]   (default: the repository)
"""

from __future__ import annotations

import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"node_modules", "screenshots", "scripts", "Presentations", "SignPath", "repo", "_site"}
SKIP_PAGES = {"mockup-dashboard.html"}
MAX_TEXT = 6000
TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"\s+")


class _Keys(HTMLParser):
    """The page's title, heading and body keys, in document order."""

    def __init__(self) -> None:
        super().__init__()
        self.title = None
        self.headings: list[str] = []
        self.keys: list[str] = []
        self.moved = False
        self.raw_title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == "meta" and attr.get("http-equiv", "").lower() == "refresh":
            self.moved = True
        if tag == "title":
            self._in_title = True
        key = attr.get("data-i18n")
        if not key or attr.get("data-i18n-attr"):
            return
        if tag == "title":
            self.title = key
        elif tag in ("h1", "h2", "h3"):
            self.headings.append(key)
        else:
            self.keys.append(key)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.raw_title += data


def _value(store: dict, key: str):
    node = store
    for part in key.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node if isinstance(node, str) else None


def _text(store: dict, fallback: dict, key: str) -> str:
    value = _value(store, key)
    if value is None or value.startswith(("[TODO]", "[MISSING")):
        value = _value(fallback, key) or ""
    return WS.sub(" ", html.unescape(TAG.sub(" ", value))).strip()


def pages(root: Path):
    for path in sorted(root.rglob("*.html")):
        if SKIP_DIRS.intersection(path.relative_to(root).parts) or path.name in SKIP_PAGES:
            continue
        parser = _Keys()
        parser.feed(path.read_text(encoding="utf-8"))
        if parser.moved or not (parser.title or parser.headings):
            continue
        url = "/" + str(path.relative_to(root)).replace("index.html", "")
        yield url, parser


def build(root: Path) -> int:
    locales = root / "assets" / "locales"
    english = json.loads((locales / "en.json").read_text(encoding="utf-8"))
    found = list(pages(root))
    out_dir = root / "assets" / "search"
    out_dir.mkdir(parents=True, exist_ok=True)
    languages = sorted(p for p in locales.glob("*.json") if not p.name.startswith("."))
    for locale in languages:
        store = json.loads(locale.read_text(encoding="utf-8"))
        entries = []
        for url, parser in found:
            headings = [h for h in (_text(store, english, k) for k in parser.headings) if h]
            # The page's own title, else its first heading, else the raw
            # <title> text (some pages' titles carry no data-i18n key).
            title = _text(store, english, parser.title) if parser.title else ""
            title = title or (headings[0] if headings else "") or parser.raw_title.strip()
            title = title.split(" - SysManage")[0] or url
            body = " ".join(t for t in (_text(store, english, k) for k in parser.keys) if t)
            entries.append({"u": url, "t": title, "h": headings[:30], "x": body[:MAX_TEXT]})
        (out_dir / locale.name).write_text(
            json.dumps(entries, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
        )
    print(f"[OK] search index: {len(found)} pages x {len(languages)} languages -> {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(build(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else REPO))
