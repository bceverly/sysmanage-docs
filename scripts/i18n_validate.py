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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i18n_no_translate import is_no_translate  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCALES_DIR = REPO_ROOT / "assets" / "locales"

# Hard limit on English-passthrough leaves per locale — i.e. the locale
# value equals the en value verbatim, a strong signal that the translator
# hasn't touched it.  Phase 10 close-out (May 2026) ratcheted this to the
# then-measured ceiling (fr=286) + a 4-key cushion = 290.
#
# June 2026: intentionally-English leaves (file paths, code/field identifiers,
# OS/product names, API tokens, version strings) are now flagged in
# ``assets/locales/no-translate.txt`` and excluded from this count entirely
# (see scripts/i18n_no_translate.py).  What remains is genuine prose plus
# Romance-language cognates that are correctly identical (French
# "Documentation"/"Architecture"/"Navigation"/"Administration"/"Description"),
# which can't be suppressed globally without hiding the same word in a language
# where it DOES differ — so they're flagged per-locale via "<lang>:" (and
# shared "<lang>,<lang>,...:") rules in no-translate.txt: French/German Latin
# cognates and the English tech loanwords European locales keep verbatim
# (Firewall, Backup, Plugin, ...).  CJK/Cyrillic/Arabic/Hindi have no Latin
# cognates, so theirs is just identity + genuine untranslated.  Binding locale
# is now nl (~76, Dutch feature labels).  Budget = ceiling + cushion.  To
# ratchet DOWN further: re-run `make translate`, and add each locale's VERIFIED
# cognates (over-flagging hides untranslated text) found with
#   python3 scripts/i18n_validate.py --report-passthrough --lang <xx>
PASSTHROUGH_BUDGET_PER_LOCALE = 90

DATA_I18N = re.compile(r'data-i18n\s*=\s*"([^"]+)"')


# Canonical locale set — anything else under ``assets/locales/`` (e.g.
# leftover ``missing_keys_analysis.json`` from a translation-pass script)
# is ignored.  Matches the 14 supported sysmanage locales.
_CANONICAL_LOCALES = frozenset({
    "ar", "de", "en", "es", "fr", "hi", "it", "ja",
    "ko", "nl", "pt", "ru", "zh_CN", "zh_TW",
})


def list_locales() -> list[str]:
    return sorted(
        p.stem for p in LOCALES_DIR.glob("*.json")
        if p.stem in _CANONICAL_LOCALES
    )


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
            passthrough = _count_passthrough(en_data, data, keys, lang)
            if passthrough > PASSTHROUGH_BUDGET_PER_LOCALE:
                print(
                    f"{lang}: {passthrough} English-passthrough leaves "
                    f"(budget {PASSTHROUGH_BUDGET_PER_LOCALE})",
                    file=sys.stderr,
                )
                failures += 1
    if failures:
        print(f"\nFAIL: {failures} issue(s)", file=sys.stderr)
        print(
            "\n"
            "How to fix\n"
            "----------\n"
            "'referenced in HTML but absent in locale' means a page uses a\n"
            "data-i18n key that some locale JSON doesn't have yet (e.g. you added\n"
            "new keys to assets/locales/en.json only). Run:\n"
            "\n"
            "  1. make i18n-seed\n"
            "       Copies each missing key into EVERY locale as a\n"
            "       '[TODO] <English text>' placeholder (from en.json), so the\n"
            "       site renders while awaiting translation.\n"
            "\n"
            "  2. make translate SERVICE=http://<host>:8765\n"
            "       Replaces the [TODO] placeholders with real translations via\n"
            "       the GPU translation service. Only untranslated strings are\n"
            "       sent, so it is idempotent — safe to re-run. Omit SERVICE to\n"
            "       use $TRANSLATION_SERVICE_URL (falls back to localhost:8765).\n"
            "\n"
            "  3. make i18n-validate\n"
            "       Re-run this check — it should now pass.\n"
            "\n"
            "An 'English-passthrough ... budget' failure instead means the keys\n"
            "exist but still hold untranslated English; run step 2 (make translate)\n"
            "to translate them, then re-validate.\n",
            file=sys.stderr,
        )
        return 1
    print("\nOK: every HTML key exists in every locale, "
          "passthrough budgets respected", file=sys.stderr)
    return 0


def _count_passthrough(
    en_data: dict, locale_data: dict, keys: set[str], lang: str
) -> int:
    """Count keys whose locale value equals the en value verbatim — a
    proxy for "translator hasn't touched this key yet".  Leaves flagged in
    no-translate.txt (globally or for ``lang``) are excluded."""
    count = 0
    for key in keys:
        en_val = lookup(en_data, key)
        loc_val = lookup(locale_data, key)
        if not isinstance(en_val, str) or not isinstance(loc_val, str):
            continue
        if (
            loc_val == en_val
            and len(en_val) > 8  # skip trivial cognates
            and not is_no_translate(key, en_val, lang)  # skip flagged leaves
        ):
            count += 1
    return count


def cmd_report_passthrough(only_lang: "str | None" = None) -> int:
    """List the still-counted passthrough leaves (English values not yet flagged
    in no-translate.txt), most-frequent first, so they can be curated.  Pass
    ``--lang xx`` to scope to one locale (useful for per-language cognates)."""
    keys = extract_html_keys()
    en_data = load_locale("en")
    counter: dict[str, int] = {}
    langs = [only_lang] if only_lang else [x for x in list_locales() if x != "en"]
    for lang in langs:
        loc = load_locale(lang)
        for key in keys:
            en_val = lookup(en_data, key)
            loc_val = lookup(loc, key)
            if (
                isinstance(en_val, str)
                and isinstance(loc_val, str)
                and loc_val == en_val
                and len(en_val) > 8
                and not is_no_translate(key, en_val, lang)
            ):
                counter[en_val] = counter.get(en_val, 0) + 1
    scope = f" for {only_lang}" if only_lang else ""
    print(f"# {len(counter)} distinct un-flagged passthrough value(s){scope}, by "
          f"count.\n# Add intentionally-English ones to assets/locales/no-translate.txt "
          f"(global, or '<lang>:' scoped for cognates).", file=sys.stderr)
    for val, n in sorted(counter.items(), key=lambda kv: -kv[1]):
        print(f"{n:4d}  {val[:100]!r}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--extract", action="store_true")
    mode.add_argument("--validate", action="store_true")
    mode.add_argument("--seed", action="store_true")
    mode.add_argument("--report-passthrough", action="store_true")
    parser.add_argument("--lang", default=None,
                        help="scope --report-passthrough to one locale")
    args = parser.parse_args()
    if args.extract:
        return cmd_extract()
    if args.report_passthrough:
        return cmd_report_passthrough(args.lang)
    return cmd_validate(seed=args.seed)


if __name__ == "__main__":
    sys.exit(main())
