#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Shared i18n "do not translate" suppression list.

JSON locale files can't carry inline ``# nosec``-style comments, so this is the
comment-like equivalent: leaves listed here are intentionally identical to
English and are excluded from BOTH:

  * the translation pass (``translate_i18n.py`` never sends them to the service), and
  * the passthrough validator (``i18n_validate.py`` never counts them).

Rules live in ``i18n-allow.txt`` (repo root — same filename as the other three
projects).  The format, including the ``<lang>:`` scope prefix used for
cognates, is documented on ``scripts/i18n_strict.py``'s ``Allow`` class, which
is now the ONE implementation.  This module is a thin compatibility shim over
it, kept so existing callers keep working.

WHY A SHIM AND NOT A SECOND PARSER (2026-08-05)
-----------------------------------------------
There used to be a full second parser here, and it disagreed with the gate's.
Its ``_known_locales()`` discovered locale names by globbing ``*.json`` next to
the rules file — but the rules file sits at the repo ROOT while the locales
live in ``assets/locales/``, so it "found" ``package.json``,
``package-lock.json`` and ``.pa11yrc.json``.  With no real locale names every
locale-scoped rule failed its validity check and fell through to the global
bucket where — still carrying its ``de:`` prefix — it was filed as a *key glob*
that could never match any key.

The visible symptom was a translation pass that could never finish: German kept
98 "gaps" on words like ``Installation`` and ``Administrator`` that the
allow-list had explicitly blessed for German, so every run re-sent them, the
service correctly returned them unchanged, and they were counted as gaps again
next run.  Meanwhile ``i18n_strict.py`` read the very same file, scoped the very
same rules correctly, and reported OK.

One file with two parsers is one file with two meanings.  Delegate.
"""
from __future__ import annotations

import importlib.util
from functools import lru_cache
from pathlib import Path
from typing import Optional

_HERE = Path(__file__).resolve().parent


@lru_cache(maxsize=1)
def _allow():
    """Load ``i18n_strict``'s allow-list reader, or die.

    Degrading to "nothing is suppressed" would silently re-send every proper
    noun to the translation service on every run and report each one as an
    unfixable gap — loud failure is cheaper than that.
    """
    cand = _HERE / "i18n_strict.py"
    if not cand.exists():
        raise SystemExit(
            f"FATAL: {cand} is missing — it owns the i18n-allow.txt format.\n"
            "  Without it every intentionally-English value is re-translated on\n"
            "  every run and reported as an unfixable gap.  Run from a full checkout."
        )
    spec = importlib.util.spec_from_file_location("_i18n_strict", cand)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Allow(mod.ALLOW_FILE)


def is_no_translate(
    dotted_key: str, en_value: Optional[str] = None, lang: Optional[str] = None
) -> bool:
    """True when this leaf is flagged intentionally-English (do not translate).

    Checks global rules always, plus any rules scoped to ``lang`` (used for
    per-language cognates).
    """
    return _allow().allows(dotted_key, en_value or "", lang)
