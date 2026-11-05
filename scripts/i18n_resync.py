#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Carry English edited in a page's HTML into the locale store.

The seeders (``i18n_validate.py --seed``, ``seed_missing_i18n.py``) only fill
keys that are absent or ``[MISSING:]``.  They never touch a key that already
holds English, so rewording a page leaves en.json -- which is what renders,
for English readers too -- saying the old thing, and the 13 translations
saying the old thing in their languages.  ``i18n-html-sync`` then fails, and
the usual fix was a one-off script per page.

For every ``data-i18n`` element in the given pages (all pages when none are
given) this script:

  * adds a key that is absent or ``[MISSING:]``: en = the HTML's English,
    every other locale = ``[TODO] <English>``;
  * resets a key whose en.json words differ from the HTML's: the same, so
    ``make translate`` retranslates it from the new English;
  * leaves a key whose words already match alone, translations included;
  * marks a markup-bearing element ``data-i18n-html``, as the seeder does.

A key carrying different English on two pages is refused: one of them is
wrong, and choosing silently would publish the wrong one.

Idempotent.  After running: ``make translate SERVICE=...`` (fills and
verifies the [TODO]s), then ``make i18n-html-sync``.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
# pylint: disable=wrong-import-position
from i18n_check_html_sync import fill_inline_parts, html_files, visible_text  # noqa: E402
from seed_missing_i18n import (  # noqa: E402
    LOCALES,
    REPO,
    _WS,
    dump,
    english_source,
    get_dotted,
    load,
    set_dotted,
)


def _words(value: str, is_html: bool) -> str:
    return _WS.sub("", visible_text(value) if is_html else value)


def collect(pages: list[Path]) -> tuple[dict[str, tuple[str, bool, str, object]], list[str]]:
    """``{key: (english, is_html, page, element)}`` and the conflicts found."""
    found: dict[str, tuple[str, bool, str, object]] = {}
    conflicts: list[str] = []
    for page in pages:
        raw = page.read_text(encoding="utf-8")
        soup = BeautifulSoup(raw, "html.parser")
        add_attr = []
        for el in soup.find_all(attrs={"data-i18n": True}):
            source = english_source(el)
            if not isinstance(source, tuple):
                continue
            key = el.get("data-i18n")
            rel = str(page.relative_to(REPO))
            if source[1] and not el.has_attr("data-i18n-html"):
                add_attr.append(key)
            if key in found:
                if _words(found[key][0], found[key][1]) != _words(*source):
                    conflicts.append(f"{key}: {found[key][2]} and {rel} differ")
                continue
            found[key] = (source[0], source[1], rel, el)
        for key in add_attr:
            raw = raw.replace(f'data-i18n="{key}"', f'data-i18n="{key}" data-i18n-html', 1)
        if add_attr:
            page.write_text(raw, encoding="utf-8")
    return found, conflicts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("pages", nargs="*", help="HTML pages (default: every page)")
    parser.add_argument("--dry-run", action="store_true", help="report only")
    args = parser.parse_args()
    pages = [Path(p).resolve() for p in args.pages] or html_files()

    found, conflicts = collect(pages)
    if conflicts:
        print("ERROR: one key, two different English texts:")
        for line in conflicts:
            print(f"  {line}")
        print("Give one of them its own key, then run this again.")
        return 1

    store = {lang: load(lang) for lang in LOCALES}
    added, reset = [], []
    for key, (english, is_html, _page, el) in found.items():
        current = get_dotted(store["en"], key)
        if isinstance(current, str) and not current.startswith("[MISSING:"):
            if current == english:
                continue
            # The same words with different markup tokens ({{c1}}) are
            # not a change of meaning: leave the translations alone.
            if _words(fill_inline_parts(current, el), True) == _words(english, is_html):
                continue
            reset.append(key)
        else:
            added.append(key)
        if args.dry_run:
            continue
        for lang in LOCALES:
            value = english if lang == "en" else f"[TODO] {english}"
            if not set_dotted(store[lang], key, value):
                print(f"ERROR: {key} is a namespace in {lang}.json, not a string")
                return 1

    if not args.dry_run and (added or reset):
        for lang in LOCALES:
            dump(lang, store[lang])
    verb = "would be" if args.dry_run else ""
    print(f"{len(added)} key(s) {verb} added, {len(reset)} {verb} reset for translation")
    for key in reset[:20]:
        print(f"  reset {key}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
