#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Gate: a translation carries its English's <code> text verbatim, and no
typographic dashes.

i18n-markup counts tags, so a translation that keeps <code>...</code> but
translates what is inside it passes -- and a reader copying the command gets
a broken one.  Measured 2026-09-24: 1,765 values across all 13 docs locales,
among them ``make test-e2e`` rendered in Korean as "unit test-E2E", ``POST``
dropped from API routes, and permission names such as ``Manage GPG Keys``
translated although the UI shows them in English.

What is compared: the multiset of <code> element contents (``<pre><code>``
blocks included) in each locale value against its en.json source.  Order is
not compared -- languages legitimately reorder a sentence.

It also fails on U+2013/U+2014 anywhere in a locale value: the project uses
ASCII hyphens only, and a translator rendering " -- " as an em dash was the
most common way one crept in (115 values the same day).
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LOCALES = REPO / "assets" / "locales"
EN = "en"
_CODE = re.compile(r"<code\b[^>]*>(.*?)</code>", re.S)
_DASH = re.compile("[–—]")


def flatten(node, prefix=""):
    for key, value in node.items():
        dotted = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            yield from flatten(value, dotted)
        elif isinstance(value, str):
            yield dotted, value


def locale_files():
    """Every translation file: ``<lang>.json`` with a language-code stem."""
    for path in sorted(LOCALES.glob("*.json")):
        if path.stem != EN and re.fullmatch(r"[a-z]{2}(?:_[A-Z]{2})?", path.stem):
            yield path


def check():
    english = dict(flatten(json.loads((LOCALES / f"{EN}.json").read_text("utf-8"))))
    code, dashes = [], []
    for path in locale_files():
        for key, value in flatten(json.loads(path.read_text("utf-8"))):
            if value.startswith("[TODO]"):
                continue  # queued: the completeness gate owns it
            if _DASH.search(value):
                dashes.append((path.stem, key))
            src = english.get(key)
            if src is not None and Counter(_CODE.findall(src)) != Counter(
                _CODE.findall(value)
            ):
                code.append((path.stem, key, _CODE.findall(src), _CODE.findall(value)))
    return code, dashes


def main() -> int:
    code, dashes = check()
    for lang, key, want, got in code[:40]:
        print(f"  [code] {lang:6} {key}\n      English: {want}\n      has:     {got}")
    for lang, key in dashes[:40]:
        print(f"  [dash] {lang:6} {key}")
    if code or dashes:
        print(
            f"\nFAIL: {len(code)} value(s) altered <code> text, "
            f"{len(dashes)} carry an en/em dash.\n"
            "  <code> content is a command, path, route or UI identifier: copy it\n"
            "  from the English byte for byte and translate only the prose around\n"
            "  it.  Replace U+2013/U+2014 with ASCII (' -- ' where the English has it)."
        )
        return 1
    print("OK: every translation keeps its English <code> text; no en/em dashes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
