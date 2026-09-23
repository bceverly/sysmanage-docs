#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""One-off remediation for hand-authored docs that bypassed i18n_autotag.py.

When a page is written with ``data-i18n="..."`` attributes already in place,
``i18n_autotag.py`` treats every element as already-tagged and never seeds the
locale store, so ``i18n_validate.py --seed`` fills each key with a
``[MISSING:<key>]`` placeholder in all 14 locales.  ``translate_i18n.py`` only
fills ``[TODO]`` gaps, so those pages can never be translated -- they render the
HTML English everywhere.

This script fixes that by, for every key whose en.json value is a
``[MISSING:...]`` placeholder:

  * extracting the element's content from the HTML -- or, when it carries
    ``data-i18n-attr="X"``, the value of attribute ``X``, because the
    runtime writes the translation there and a void element like
    ``<meta>`` has no content to read,
  * if the element contains inline markup (``<code>``, ``<strong>``, ...),
    marking it ``data-i18n-html`` and storing the inner HTML (so the runtime
    uses ``innerHTML``); otherwise storing plain text (``textContent``),
  * writing en.json = English and the 13 other locales = ``[TODO] <English>``.

Idempotent: only ``[MISSING:...]`` / absent leaves are touched -- real
translations and existing ``[TODO]`` gaps are left alone.  After running,
``make translate`` fills the fresh ``[TODO]`` gaps on the GPU service.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

REPO = Path(__file__).resolve().parent.parent
LOCALES_DIR = REPO / "assets" / "locales"
LOCALES = [
    "ar", "de", "en", "es", "fr", "hi", "it",
    "ja", "ko", "nl", "pt", "ru", "zh_CN", "zh_TW",
]
_WS = re.compile(r"\s+")


def collapse(text: str) -> str:
    return _WS.sub(" ", text).strip()


#: english_source() results that are not a value.
SKIP_NESTED = "nested"
SKIP_EMPTY_ATTR = "empty-attr"


def english_source(el) -> "tuple[str, bool] | str":
    """The English an element's markup carries, as the runtime would place it.

    Returns ``(value, is_html)``, or SKIP_NESTED / SKIP_EMPTY_ATTR.  The one
    reader of HTML English: the seeder and the HTML/en.json sync gate
    (i18n_check_html_sync.py) both ask it, so they cannot disagree about what
    a page says.
    """
    # ATTRIBUTE-VALUED KEYS FIRST.  ``data-i18n-attr="content"`` tells
    # the runtime to write the translation into that ATTRIBUTE rather
    # than into the element, and the canonical English therefore lives
    # in the attribute too.  <meta> is a void element, so both
    # decode_contents() and get_text() return "" for it -- which is
    # exactly what got written: 21 meta descriptions sat empty in
    # en.json, invisible to every gate (an empty string is not
    # [MISSING:], not [TODO] and not English-identical), so no page's
    # description was ever translated in any locale.
    i18n_attr = el.get("data-i18n-attr")
    if i18n_attr:
        source = collapse(el.get(i18n_attr) or "")
        if not source:
            return SKIP_EMPTY_ATTR
        # An attribute value is plain text by definition -- it cannot
        # carry markup for innerHTML, so it never gets data-i18n-html.
        return (source, False)

    inner = collapse(el.decode_contents())
    # Refuse to swallow a nested translation scope.
    if "data-i18n" in inner:
        return SKIP_NESTED
    if "<" in inner:  # element carries inline markup
        return (inner, True)
    return (collapse(el.get_text(" ")), False)


def walk(obj, prefix=""):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from walk(value, f"{prefix}.{key}" if prefix else key)
    else:
        yield prefix, obj


def get_dotted(data: dict, dotted: str):
    cur = data
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def set_dotted(data: dict, dotted: str, value) -> bool:
    parts = dotted.split(".")
    cur = data
    for part in parts[:-1]:
        nxt = cur.get(part)
        if not isinstance(nxt, dict):
            if nxt is not None:
                return False
            nxt = {}
            cur[part] = nxt
        cur = nxt
    cur[parts[-1]] = value
    return True


def load(lang: str) -> dict:
    return json.loads((LOCALES_DIR / f"{lang}.json").read_text(encoding="utf-8"))


def dump(lang: str, data: dict) -> None:
    (LOCALES_DIR / f"{lang}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    en = load("en")
    # EMPTY counts as missing, not just the [MISSING:] placeholder. An empty
    # English value is the more dangerous of the two precisely because it is
    # invisible: it is not [MISSING:], not [TODO] and not English-identical,
    # so every gate passes it. That is how 21 meta descriptions shipped
    # untranslated in 13 locales without a single check complaining.
    missing = {
        k for k, v in walk(en)
        if isinstance(v, str) and (v.startswith("[MISSING:") or not v.strip())
    }
    print(f"{len(missing)} missing/empty key(s) in en.json")

    html_files = [
        p for p in REPO.rglob("*.html")
        if "node_modules" not in p.parts
        and not any(part.startswith(".") for part in p.parts)
    ]

    extracted: dict[str, tuple[str, bool]] = {}  # key -> (value, is_html)
    skipped_nested = []
    skipped_empty_attr = []
    for hp in html_files:
        raw = hp.read_text(encoding="utf-8")
        soup = BeautifulSoup(raw, "html.parser")
        add_attr: list[str] = []
        for el in soup.find_all(attrs={"data-i18n": True}):
            key = el.get("data-i18n")
            if key not in missing or key in extracted:
                continue
            source = english_source(el)
            if source == SKIP_NESTED:
                skipped_nested.append(key)
            elif source == SKIP_EMPTY_ATTR:
                skipped_empty_attr.append((key, el.get("data-i18n-attr")))
            else:
                extracted[key] = source
                if source[1] and not el.has_attr("data-i18n-html"):
                    add_attr.append(key)
        # Surgically add data-i18n-html to markup-bearing elements.
        if add_attr:
            for key in add_attr:
                needle = f'data-i18n="{key}"'
                if needle in raw and not re.search(
                    re.escape(needle) + r"(?=[^>]*data-i18n-html)", raw
                ):
                    raw = raw.replace(needle, needle + " data-i18n-html", 1)
            hp.write_text(raw, encoding="utf-8")
            print(f"  +data-i18n-html: {hp.relative_to(REPO)} ({len(add_attr)})")

    print(f"extracted {len(extracted)} keys from HTML")
    if skipped_nested:
        print(f"skipped {len(skipped_nested)} nested-scope keys: {skipped_nested}")
    if skipped_empty_attr:
        # The attribute the key points at is itself empty in the HTML, so
        # there is no English to seed. Reported rather than silently written
        # as "", which is the failure this whole branch exists to prevent.
        print(f"skipped {len(skipped_empty_attr)} key(s) whose target attribute "
              f"is empty in the HTML: {skipped_empty_attr}")
    orphan = missing - set(extracted) - set(skipped_nested)
    if orphan:
        print(f"WARN: {len(orphan)} [MISSING] keys have no HTML element (left as-is)")

    for lang in LOCALES:
        data = load(lang)
        n = 0
        for key, (val, _ishtml) in extracted.items():
            cur = get_dotted(data, key)
            # Same widening as the trigger above: an EMPTY value is a gap, and
            # overwriting it is safe precisely because it holds nothing. A real
            # translation or an existing [TODO] is still left alone.
            if cur is None or (
                isinstance(cur, str)
                and (cur.startswith("[MISSING:") or not cur.strip())
            ):
                if set_dotted(data, key, val if lang == "en" else f"[TODO] {val}"):
                    n += 1
        dump(lang, data)
        print(f"  {lang}: seeded {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
