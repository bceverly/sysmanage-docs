#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Shared i18n "do not translate" suppression list.

JSON locale files can't carry inline ``# nosec``-style comments, so this is the
comment-like equivalent: leaves listed here are intentionally identical to
English and are excluded from BOTH:

  * the translation pass (``translate_i18n.py`` never sends them to the service), and
  * the passthrough validator (``i18n_validate.py`` never counts them toward the
    per-locale English-passthrough budget).

Rules live in ``assets/locales/no-translate.txt``, one per line:

    # a full-line comment (the line starts with '#')
    administration.host_management.agent_deployment   exact dotted key (global)
    api.reference.endpoints.*                          fnmatch glob on the key
    re:^/                                              regex on the ENGLISH value

A rule may be **locale-scoped** by prefixing it with ``<lang>:`` — it then
applies only to that locale.  This is how cross-language **cognates** are
flagged: a word that is correctly identical to English in one language but must
differ in another (French "Documentation" is right as-is, German needs
"Dokumentation"):

    fr: re:^(Documentation|Architecture|Navigation)$
    fr: some.specific.key

Un-prefixed rules are global (every locale).  A leaf is suppressed for a given
locale when it matches any global rule OR any rule scoped to that locale.  Keep
value regexes tight (anchored) so they don't suppress real prose.
"""
from __future__ import annotations

import fnmatch
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_RULES_PATH = (
    Path(__file__).resolve().parent.parent / "assets" / "locales" / "no-translate.txt"
)

# A bucket of rules: (key globs, compiled value regexes).
_Bucket = Tuple[List[str], List["re.Pattern[str]"]]


@lru_cache(maxsize=1)
def _known_locales() -> frozenset:
    base = _RULES_PATH.parent
    return frozenset(p.stem for p in base.glob("*.json")) - {"en"}


@lru_cache(maxsize=1)
def _load() -> Tuple[_Bucket, Dict[str, _Bucket]]:
    glob_keys: List[str] = []
    glob_res: List["re.Pattern[str]"] = []
    per_lang: Dict[str, _Bucket] = {}
    locales = _known_locales()
    if not _RULES_PATH.exists():
        return (glob_keys, glob_res), per_lang
    for raw in _RULES_PATH.read_text(encoding="utf-8").splitlines():
        # Drop an inline comment (whitespace + '#'); a line that is only a
        # comment starts with '#'.  Regexes rarely contain a literal ' #'.
        line = re.split(r"\s#", raw, maxsplit=1)[0].strip()
        if not line or line.startswith("#"):
            continue
        # Optional "<lang>:" (or "<lang>,<lang>,...:") scope prefix.  ``re:`` is
        # NOT a locale, so a global value regex is never mistaken for a scoped
        # rule.  The same rule may target several locales (shared loanwords).
        head, sep, rest = line.partition(":")
        heads = [h.strip() for h in head.split(",")] if sep else []
        if heads and all(h in locales for h in heads):
            buckets = [per_lang.setdefault(h, ([], [])) for h in heads]
            line = rest.strip()
        else:
            buckets = [(glob_keys, glob_res)]
        if not line:
            continue
        if line.startswith("re:"):
            try:
                pattern = re.compile(line[3:])
            except re.error:
                continue  # a malformed pattern must not break the pipeline
            for _keys, res in buckets:
                res.append(pattern)
        else:
            for keys, _res in buckets:
                keys.append(line)
    return (glob_keys, glob_res), per_lang


def _matches(bucket: _Bucket, dotted_key: str, en_value: Optional[str]) -> bool:
    key_globs, value_res = bucket
    for glob in key_globs:
        if fnmatch.fnmatchcase(dotted_key, glob):
            return True
    if en_value is not None:
        for pattern in value_res:
            if pattern.search(en_value):
                return True
    return False


def is_no_translate(
    dotted_key: str, en_value: Optional[str] = None, lang: Optional[str] = None
) -> bool:
    """True when this leaf is flagged intentionally-English (do not translate).

    Checks global rules always, plus any rules scoped to ``lang`` (used for
    per-language cognates).
    """
    global_bucket, per_lang = _load()
    if _matches(global_bucket, dotted_key, en_value):
        return True
    if lang and lang in per_lang and _matches(per_lang[lang], dotted_key, en_value):
        return True
    return False
