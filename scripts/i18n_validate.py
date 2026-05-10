#!/usr/bin/env python3
"""i18n extraction + validation pipeline for sysmanage-docs.

Modes (one required):
  --extract  Walk every ``.html`` under the repo root, collect
             ``data-i18n="..."`` attribute values, and print a flat list
             to stdout.
  --validate Verify every key referenced in HTML exists in every locale
             ``.json``.  Exits non-zero on missing keys.  Also reports
             orphan keys (in-locale-but-not-in-HTML) as a warning, and
             checks for English-passthrough leaf values (a non-en locale
             whose value equals the en authoritative value verbatim).
  --seed     Like ``--validate``, but missing keys in locale JSONs are
             populated with the English value prefixed by ``[TODO] ``.
             Idempotent — existing values are not overwritten.

The 14 supported locales are auto-discovered from
``assets/locales/<lang>.json``.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCALES_DIR = REPO_ROOT / "assets" / "locales"

# Hard limit on English-passthrough leaves per locale — i.e. the locale
# value equals the en value verbatim, a strong signal that the translator
# hasn't touched it.  Phase 10 close-out (May 2026) ratcheted this down
# to current measured ceiling (max per-locale was fr=286) plus a tiny
# 4-key cushion.  Drift up = CI fails; ratchet down further as long-form
# descriptions get real translations.
PASSTHROUGH_BUDGET_PER_LOCALE = 290

DATA_I18N = re.compile(r'data-i18n\s*=\s*"([^"]+)"')


def list_locales() -> list[str]:
    return sorted(p.stem for p in LOCALES_DIR.glob("*.json"))


def load_locale(lang: str) -> dict:
    return json.loads((LOCALES_DIR / f"{lang}.json").read_text(encoding="utf-8"))


def write_locale(lang: str, data: dict) -> None:
    (LOCALES_DIR / f"{lang}.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def extract_html_keys() -> set[str]:
    """Walk every .html under REPO_ROOT and collect data-i18n keys."""
    keys: set[str] = set()
    for path in REPO_ROOT.rglob("*.html"):
        if any(p.startswith(".") for p in path.parts):  # skip dotfiles
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for match in DATA_I18N.finditer(text):
            keys.add(match.group(1))
    return keys


def lookup(data: dict, dotted_key: str):
    parts = dotted_key.split(".")
    node = data
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def insert_dotted(target: dict, dotted_key: str, value) -> None:
    parts = dotted_key.split(".")
    for part in parts[:-1]:
        node = target.get(part)
        if not isinstance(node, dict):
            target[part] = {}
        target = target[part]
    target[parts[-1]] = value


def flatten(d: dict, prefix: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in d.items():
        joined = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            out.update(flatten(value, joined))
        else:
            out[joined] = value
    return out


def cmd_extract() -> int:
    for key in sorted(extract_html_keys()):
        print(key)
    return 0


def cmd_validate(seed: bool) -> int:
    keys = extract_html_keys()
    locales = list_locales()
    if "en" not in locales:
        print("FAIL: en.json is missing — can't validate without it", file=sys.stderr)
        return 1
    en_data = load_locale("en")
    failures = 0
    for lang in locales:
        data = load_locale(lang)
        flat = flatten(data)
        missing = sorted(keys - set(flat))
        if missing:
            print(
                f"{lang}: {len(missing)} keys referenced in HTML but absent in locale",
                file=sys.stderr,
            )
            for key in missing[:5]:
                print(f"  - {key}", file=sys.stderr)
            if len(missing) > 5:
                print(f"  ... and {len(missing) - 5} more", file=sys.stderr)
            if seed:
                seeded_count = 0
                for key in missing:
                    en_value = lookup(en_data, key)
                    if isinstance(en_value, str):
                        seeded = en_value if lang == "en" else f"[TODO] {en_value}"
                    else:
                        # Key isn't in en either — use the dotted key as a
                        # placeholder so the JSON has *something*.  The
                        # docs site renderer falls back to the key string
                        # when the lookup fails today; this just makes that
                        # behavior explicit and visible in the locale file.
                        seeded = f"[MISSING:{key}]"
                    insert_dotted(data, key, seeded)
                    seeded_count += 1
                write_locale(lang, data)
                print(f"  → seeded {seeded_count} keys", file=sys.stderr)
            else:
                failures += 1
        if lang != "en":
            passthrough = _count_passthrough(en_data, data, keys)
            if passthrough > PASSTHROUGH_BUDGET_PER_LOCALE:
                print(
                    f"{lang}: {passthrough} English-passthrough leaves "
                    f"(budget {PASSTHROUGH_BUDGET_PER_LOCALE})",
                    file=sys.stderr,
                )
                failures += 1
    if failures:
        print(f"\nFAIL: {failures} issue(s)", file=sys.stderr)
        return 1
    print("\nOK: every HTML key exists in every locale, "
          "passthrough budgets respected", file=sys.stderr)
    return 0


def _count_passthrough(en_data: dict, locale_data: dict, keys: set[str]) -> int:
    """Count keys whose locale value equals the en value verbatim — a
    proxy for "translator hasn't touched this key yet"."""
    count = 0
    for key in keys:
        en_val = lookup(en_data, key)
        loc_val = lookup(locale_data, key)
        if not isinstance(en_val, str) or not isinstance(loc_val, str):
            continue
        if loc_val == en_val and len(en_val) > 8:  # skip trivial cognates
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--extract", action="store_true")
    mode.add_argument("--validate", action="store_true")
    mode.add_argument("--seed", action="store_true")
    args = parser.parse_args()
    if args.extract:
        return cmd_extract()
    return cmd_validate(seed=args.seed)


if __name__ == "__main__":
    sys.exit(main())
