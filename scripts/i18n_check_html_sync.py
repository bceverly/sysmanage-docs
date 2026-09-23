#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Gate: a page's English must say what en.json says.

``assets/js/i18n.js`` renders every ``data-i18n`` element from the locale
store -- for English readers too, from en.json.  The English written in the
HTML is only a fallback, so editing it changes nothing a reader sees, and
nothing else notices: i18n-validate asks whether the key exists, i18n-strict
compares locales against en.json, and neither ever reads the page.

Measured 2026-09-23: 281 values on 40 pages where the HTML and en.json said
different things -- the roadmap listing shipped features as still ahead among
them -- plus 691 where the HTML carried em/en dashes that en.json had already
made ASCII.  This gate fails on any such pair, so the edit has to land in both.

What is compared is the TEXT a reader gets, modeled on i18n.js: the en.json
value has its ``{{cN}}`` tokens filled from the element's own code/strong/em
children (fillInlineParts), then both sides lose their tags, decode entities
and collapse whitespace.  The HTML side is read by
seed_missing_i18n.english_source(), the same reader the seeder uses, so the
two cannot disagree about what a page says.

Formatting is NOT gated.  Where the HTML wraps words in <strong>/<code> and
en.json carries the same words bare, the reader loses the formatting, not the
meaning; that is counted and reported (--markup-report) as a separate backlog,
along with the stray spaces ("Bandit : Python") that autotag's text extraction
left where it stripped a tag.

    python3 scripts/i18n_check_html_sync.py            # gate
    python3 scripts/i18n_check_html_sync.py --json F   # write the mismatches to F
    python3 scripts/i18n_check_html_sync.py --markup-report  # formatting-only losses
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from seed_missing_i18n import (  # noqa: E402  pylint: disable=wrong-import-position
    REPO,
    english_source,
    get_dotted,
    load,
)

_WS = re.compile(r"\s+")
_TAG = re.compile(r"<[^>]+>")
# Tags that break a line: they separate words, so they read as a space.  Every
# other tag (code, strong, a, span, ...) sits inside a run of text and must not
# add one, or "<code>x</code>." compares unequal to "x.".
_BLOCK_TAG = re.compile(r"</?(?:br|p|div|li|ul|ol|tr|td|th|h[1-6]|dt|dd)\b[^>]*>", re.I)
_INLINE_TOKEN = re.compile(r"\{\{c(\d+)\}\}")


def fill_inline_parts(value: str, el) -> str:
    """i18n.js fillInlineParts(): {{cN}} -> the Nth code/strong/em child."""
    if not _INLINE_TOKEN.search(value):
        return value
    parts = [str(node) for node in el.select("code, strong, em")]

    def part(match: re.Match) -> str:
        index = int(match.group(1)) - 1
        return parts[index] if 0 <= index < len(parts) else match.group(0)

    return _INLINE_TOKEN.sub(part, value)


def visible_text(fragment: str) -> str:
    """The words a reader gets, give or take whitespace the browser collapses."""
    text = _TAG.sub("", _BLOCK_TAG.sub(" ", fragment))
    return _WS.sub(" ", html.unescape(text)).strip()


def normalize(fragment: str) -> str:
    """Markup-preserving form, for the formatting report."""
    return _WS.sub(" ", html.unescape(fragment)).strip()


def html_files() -> list[Path]:
    """Every page, walked the way the seeder walks them."""
    return sorted(
        p for p in REPO.rglob("*.html")
        if "node_modules" not in p.parts
        and not any(part.startswith(".") for part in p.parts)
    )


def find_mismatches() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """(text mismatches -- gated, formatting-only differences -- reported)."""
    en = load("en")
    found: list[dict[str, str]] = []
    formatting: list[dict[str, str]] = []
    for path in html_files():
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        for el in soup.find_all(attrs={"data-i18n": True}):
            source = english_source(el)
            if not isinstance(source, tuple):
                continue  # nested scope / empty attribute: nothing to compare
            key = el.get("data-i18n")
            value = get_dotted(en, key)
            if not isinstance(value, str) or value.startswith("[MISSING:"):
                continue  # absence is i18n-validate's job, not this gate's
            rendered = fill_inline_parts(value, el)
            # A plain-text source is already decoded ("<package>" is literal
            # text there, not a tag), so only a markup source is stripped.
            page_words = visible_text(source[0]) if source[1] else _WS.sub(" ", source[0])
            item = {
                "file": str(path.relative_to(REPO)),
                "key": key,
                "html": source[0],
                "en": value,
            }
            # Words only: whitespace differences are autotag's get_text(" ")
            # leaving "Bandit : Python" where the markup had none -- the same
            # stored-without-its-markup defect as lost formatting, so they
            # are reported with it rather than gated.
            if _WS.sub("", page_words) != _WS.sub("", visible_text(rendered)):
                found.append(item)
            elif normalize(source[0]) != normalize(rendered):
                formatting.append(item)
    return found, formatting


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--json", metavar="FILE", help="write mismatches to FILE")
    parser.add_argument("--markup-report", action="store_true",
                        help="list formatting-only differences (not gated)")
    args = parser.parse_args()

    found, formatting = find_mismatches()
    if args.json:
        Path(args.json).write_text(
            json.dumps(found, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    if args.markup_report:
        for item in formatting:
            print(f"  {item['file']}  {item['key']}")
        print(f"{len(formatting)} value(s) render without the HTML's formatting")
        return 0
    if not found:
        print("OK: every page's English matches en.json"
              + (f" ({len(formatting)} formatting-only difference(s) not gated;"
                 " see --markup-report)" if formatting else ""))
        return 0

    by_file: dict[str, int] = {}
    for item in found:
        by_file[item["file"]] = by_file.get(item["file"], 0) + 1
    for item in found[:10]:
        print(f"  {item['file']}  {item['key']}")
        print(f"      html: {visible_text(item['html'])[:110]}")
        print(f"      en:   {visible_text(item['en'])[:110]}")
    if len(found) > 10:
        print(f"  ... and {len(found) - 10} more")
    print(f"\nFAIL: {len(found)} value(s) on {len(by_file)} page(s) where the HTML "
          "and en.json disagree.\n"
          "  Readers see en.json, so the HTML edit is invisible until both match.\n"
          "  Decide which side is current, make the other say the same, then\n"
          "  requeue + translate (make i18n-fix) so the 13 locales follow.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
