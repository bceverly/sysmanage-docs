#!/usr/bin/env python3
"""Phase 11.7 structural i18n auto-tagger for sysmanage-docs.

Walks every ``.html`` under the repo root and adds ``data-i18n="<key>"``
attributes to every text-bearing tag that doesn't already have one.

Key shape: ``docs.auto.<relative-path-with-slashes-as-dots>.<stable-id>``
where ``<stable-id>`` is a zero-padded counter (``001``, ``002``, ...)
scoped to the file in document order.  Auto-generated structural keys
live under the dedicated ``docs.auto.*`` namespace, distinct from the
hand-curated ``docs.<section>.<page>`` semantic keys (e.g. the docs
landing page already references ``docs.security.authentication`` as a
flat link-label leaf; sharing that namespace would clobber the leaf in
JSON because a dotted path can't be both a leaf and a parent).

Design choice: keys are stable IDs, not content hashes.  Re-runs of this
script produce the same key for the same source element provided the
structural order is unchanged.  Elements that already carry a
``data-i18n`` attribute are preserved untouched, and the counter only
allocates new IDs for newly-tagged elements — so existing tagged content
keeps its key even if surrounding untagged text moves.  If you reorder
HTML across re-runs, expect the IDs assigned to NEW elements to shift;
this is intentional (content-hash keys would churn every typo fix).

The script also seeds the 14 locale JSONs under ``assets/locales/`` with:
  - en.json: verbatim English source text (whitespace-collapsed)
  - 13 others: ``[TODO] <English text>`` placeholder

Translation is explicitly NOT performed here — Phase 12 owns that pass.

This script is idempotent: a second run on already-tagged files is a
no-op.

Constraints:
  - Skips elements inside <script>, <style>, <pre>, <code> blocks.
  - Skips elements whose ancestors already carry a ``data-i18n`` attribute
    (so a tagged <li> does not also tag its descendant <strong>).
  - Skips elements whose visible text (after whitespace collapse) is empty.
  - Preserves source formatting via surgical in-place attribute insertion
    keyed off BeautifulSoup's ``sourceline`` / ``sourcepos``; never calls
    ``soup.prettify()`` or ``str(soup)`` on the whole document.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCALES_DIR = REPO_ROOT / "assets" / "locales"

TAGGABLE = {
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "li", "td", "th",
    "span", "strong", "em", "a", "button", "label",
    "summary", "figcaption", "caption", "dt", "dd", "blockquote",
}

# Walking into any of these halts traversal — text inside them is content,
# not prose.
SKIP_DESCENDANTS_OF = {"script", "style", "pre", "code"}

LOCALES = ("ar", "de", "en", "es", "fr", "hi", "it", "ja",
           "ko", "nl", "pt", "ru", "zh_CN", "zh_TW")

# Open-tag regex, anchored at start.  Captures the tag's own attrs region.
# We deliberately match a single open tag like ``<p class="foo">`` —
# this is applied at a known offset, not a free scan.
_OPEN_TAG_RE = re.compile(
    r"<([A-Za-z][A-Za-z0-9]*)([^>]*?)(/?)>",
    re.DOTALL,
)

_WS_RE = re.compile(r"\s+")


def relpath_to_key_prefix(html_path: Path) -> str:
    """Map repo-relative HTML path to dotted key prefix.

    All auto-tagged keys live under ``docs.auto.*`` so they cannot
    collide with hand-curated keys in the ``docs.<section>.<page>``
    namespace (e.g. the flat ``docs.security.authentication`` link
    label on the docs landing page).

    Leading ``docs/`` is stripped from the relative path so keys don't
    double up (``docs.auto.docs.foo.NNN``).  Sibling-of-``docs/`` pages
    (index.html, flatpak.html, etc.) get a ``home.`` infix.

    Examples:
        docs/installation/ubuntu.html  -> docs.auto.installation.ubuntu
        docs/index.html                -> docs.auto.index
        index.html                     -> docs.auto.home.index
        flatpak.html                   -> docs.auto.home.flatpak
        repo/deb/index.html            -> docs.auto.repo.deb.index
    """
    rel = html_path.relative_to(REPO_ROOT)
    parts = list(rel.parts)
    # Strip .html from final part.
    parts[-1] = parts[-1][:-len(".html")]
    if parts and parts[0] == "docs":
        parts = parts[1:]
    elif parts and parts[0] not in ("repo",):
        # Top-level (sibling-of-docs) pages — namespace them under ``home``
        # so they don't collide with subdir names at the same depth.
        parts = ["home"] + parts
    return "docs.auto." + ".".join(parts)


def collapse_ws(text: str) -> str:
    return _WS_RE.sub(" ", text).strip()


def ancestor_has_i18n(tag) -> bool:
    """True if any ancestor (excluding the tag itself) has data-i18n."""
    cur = tag.parent
    while cur is not None and getattr(cur, "name", None) is not None:
        if cur.has_attr("data-i18n"):
            return True
        cur = cur.parent
    return False


def descendant_has_i18n(tag) -> bool:
    """True if any descendant carries data-i18n.

    If a descendant is already tagged, tagging this ancestor would create
    overlapping translation scopes (the ancestor key would re-translate
    the descendant's content, conflicting with the descendant's own key).
    Skip the ancestor in that case.
    """
    for desc in tag.descendants:
        if hasattr(desc, "has_attr") and desc.has_attr("data-i18n"):
            return True
    return False


def ancestor_in_skip(tag) -> bool:
    """True if any ancestor is a script/style/pre/code block."""
    cur = tag.parent
    while cur is not None and getattr(cur, "name", None) is not None:
        if cur.name in SKIP_DESCENDANTS_OF:
            return True
        cur = cur.parent
    return False


def visible_text(tag) -> str:
    """Get the tag's visible text, ignoring text inside <script>/<style>.

    BS4's ``get_text()`` already concatenates descendant strings — we just
    collapse whitespace.  For our eligibility check this is sufficient.
    """
    return collapse_ws(tag.get_text(separator=" "))


def inner_html_collapsed(raw: str, start: int, end: int) -> str:
    """Return whitespace-collapsed inner HTML between two byte offsets."""
    return collapse_ws(raw[start:end])


def find_open_tag_end(raw: str, line: int, col: int) -> tuple[int, int, str, str] | None:
    """Locate the open tag at (line, col) in raw text.

    Returns (start_offset, end_offset, tagname, attrs_text) or None if
    the tag could not be located (e.g. position is bogus, or the tag is
    self-closing in a way we can't handle).

    ``col`` is 0-based per BS4's sourcepos.
    """
    # Convert (line, col) into a byte offset.  Lines are 1-based.
    lines_seen = 0
    offset = 0
    for i, ch in enumerate(raw):
        if lines_seen == line - 1:
            offset = i + col
            break
        if ch == "\n":
            lines_seen += 1
    else:
        # Either we never found line-1 newlines (file is shorter than
        # expected) or the start is on line 1.
        if line == 1:
            offset = col
        else:
            return None

    if offset >= len(raw) or raw[offset] != "<":
        # BS4 sometimes reports sourcepos pointing just past the ``<``.
        if offset > 0 and raw[offset - 1] == "<":
            offset -= 1
        else:
            return None

    m = _OPEN_TAG_RE.match(raw, offset)
    if not m:
        return None
    return offset, m.end(), m.group(1).lower(), m.group(2)


def matching_close_offset(raw: str, open_end: int, tagname: str) -> int | None:
    """Find the offset of the matching </tagname> for the open tag.

    Uses naive depth counting on the raw string after ``open_end``.  This
    is good enough for well-formed HTML.  Skips nested same-name tags.
    """
    pattern = re.compile(
        r"<\s*(/?)\s*" + re.escape(tagname) + r"(\s|>|/)",
        re.IGNORECASE,
    )
    depth = 1
    pos = open_end
    while pos < len(raw):
        m = pattern.search(raw, pos)
        if not m:
            return None
        is_close = m.group(1) == "/"
        if is_close:
            depth -= 1
            if depth == 0:
                return m.start()
        else:
            depth += 1
        pos = m.end()
    return None


def process_file(
    html_path: Path,
    en_translations: dict[str, str],
) -> tuple[int, int]:
    """Tag eligible elements in one HTML file.

    Returns (added_count, skipped_count).
    """
    raw = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(raw, "html.parser")

    key_prefix = relpath_to_key_prefix(html_path)
    # Stable counter: scan existing data-i18n keys that follow our shape
    # ``<prefix>.NNN`` and pick the next free ID so re-runs don't collide.
    existing_ids: set[int] = set()
    for tag in soup.find_all(attrs={"data-i18n": True}):
        val = tag.get("data-i18n", "")
        if val.startswith(key_prefix + "."):
            suffix = val[len(key_prefix) + 1:]
            if suffix.isdigit():
                existing_ids.add(int(suffix))
    next_id = 1
    while next_id in existing_ids:
        next_id += 1

    # Plan edits: list of (offset, key).  Offset points at the ``>`` of
    # the open tag — we insert ``\x20data-i18n="<key>"`` just before it.
    edits: list[tuple[int, str]] = []
    added = 0
    skipped = 0

    # Walk in document order via descendants iteration.  ``soup.descendants``
    # yields strings + tags; we filter to tags.
    for tag in soup.descendants:
        if not hasattr(tag, "name") or tag.name is None:
            continue
        if tag.name not in TAGGABLE:
            continue
        if tag.has_attr("data-i18n"):
            continue
        if ancestor_in_skip(tag):
            continue
        if ancestor_has_i18n(tag):
            # Parent will be tagged; don't double-tag inline descendants.
            continue
        if descendant_has_i18n(tag):
            # A child (or deeper) already has its own translation key —
            # tagging this ancestor would create an overlapping scope.
            continue
        text = visible_text(tag)
        if not text:
            continue
        # Skip pure-whitespace / icon-only spans whose collapsed text is
        # a single glyph (no letters/digits at all).  These are typically
        # icon glyphs like &#11088; that shouldn't go through translation.
        if not re.search(r"[A-Za-z0-9]", text):
            skipped += 1
            continue

        # Locate the open tag in the source.
        if tag.sourceline is None or tag.sourcepos is None:
            skipped += 1
            continue
        located = find_open_tag_end(raw, tag.sourceline, tag.sourcepos)
        if located is None:
            skipped += 1
            continue
        tag_start, tag_end, parsed_name, attrs_text = located
        if parsed_name != tag.name:
            # Source/parse mismatch — bail out on this element.
            skipped += 1
            continue

        # Allocate ID.
        key_id = f"{next_id:03d}"
        next_id += 1
        while next_id in existing_ids:
            next_id += 1
        key = f"{key_prefix}.{key_id}"

        edits.append((tag_end - 1, key))
        # Mutate the tree too — so descendant traversal sees this tag as
        # tagged and skips its inline children.
        tag["data-i18n"] = key
        en_translations[key] = text
        added += 1

    if not edits:
        return 0, skipped

    # Apply edits in reverse offset order so earlier positions stay valid.
    chunks: list[str] = []
    cursor = len(raw)
    for offset, key in sorted(edits, key=lambda e: -e[0]):
        # ``offset`` points at the ``>`` (or ``/`` for self-closing) of
        # the open tag.  Insert ``\x20data-i18n="<key>"`` just before it.
        insertion = f' data-i18n="{key}"'
        chunks.append(raw[offset:cursor])
        chunks.append(insertion)
        cursor = offset
    chunks.append(raw[:cursor])
    new_raw = "".join(reversed(chunks))
    html_path.write_text(new_raw, encoding="utf-8")
    return added, skipped


def load_locale(lang: str) -> dict:
    return json.loads((LOCALES_DIR / f"{lang}.json").read_text(encoding="utf-8"))


def write_locale(lang: str, data: dict) -> None:
    (LOCALES_DIR / f"{lang}.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def insert_dotted(target: dict, dotted_key: str, value) -> bool:
    """Insert value at dotted key path.  Returns True if a new leaf was
    written; False if a leaf was already present (no overwrite) or if
    insertion would clobber a non-dict ancestor.

    NB: refuses to promote an existing string leaf into a dict — that
    would silently lose the original value.  Auto-tagged keys all live
    under the dedicated ``docs.auto.*`` namespace specifically to avoid
    such collisions.
    """
    parts = dotted_key.split(".")
    for i, part in enumerate(parts[:-1]):
        node = target.get(part)
        if node is None:
            target[part] = {}
        elif not isinstance(node, dict):
            # Refuse to clobber a non-dict leaf.  Caller should pick a
            # different key path.
            sys.stderr.write(
                f"WARN: refusing to promote leaf at "
                f"{'.'.join(parts[:i+1])!r} into a dict (would lose value "
                f"{node!r}); skipping {dotted_key!r}\n"
            )
            return False
        target = target[part]
    leaf = parts[-1]
    if leaf in target and not isinstance(target[leaf], dict):
        return False
    if leaf in target and isinstance(target[leaf], dict):
        # Existing subtree at the leaf position — can't write a string.
        sys.stderr.write(
            f"WARN: leaf position {dotted_key!r} already holds a subtree; "
            f"skipping\n"
        )
        return False
    target[leaf] = value
    return True


def seed_locales(en_translations: dict[str, str]) -> dict[str, int]:
    """Seed all 14 locale files with the new keys.

    Returns per-locale count of newly-seeded keys.
    """
    counts: dict[str, int] = {}
    for lang in LOCALES:
        data = load_locale(lang)
        added = 0
        for key, en_text in en_translations.items():
            if lang == "en":
                value = en_text
            else:
                value = f"[TODO] {en_text}"
            if insert_dotted(data, key, value):
                added += 1
        write_locale(lang, data)
        counts[lang] = added
    return counts


def main() -> int:
    html_files = sorted(
        p for p in REPO_ROOT.rglob("*.html")
        if "node_modules" not in p.parts
        and not any(part.startswith(".") for part in p.parts)
    )
    print(f"Found {len(html_files)} HTML files", file=sys.stderr)

    en_translations: dict[str, str] = {}
    total_added = 0
    total_skipped = 0
    files_modified = 0
    for path in html_files:
        added, skipped = process_file(path, en_translations)
        total_added += added
        total_skipped += skipped
        if added:
            files_modified += 1
            print(f"  {path.relative_to(REPO_ROOT)}: +{added}", file=sys.stderr)

    print(
        f"\nTagged {total_added} elements across {files_modified} files "
        f"({total_skipped} candidates skipped)",
        file=sys.stderr,
    )

    if not en_translations:
        print("No new keys to seed.", file=sys.stderr)
        return 0

    print(f"\nSeeding {len(en_translations)} new keys into 14 locales...",
          file=sys.stderr)
    counts = seed_locales(en_translations)
    for lang in LOCALES:
        print(f"  {lang}: +{counts[lang]}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
