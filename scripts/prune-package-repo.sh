#!/usr/bin/env bash
#
# Prune the committed multi-format package repository under ./repo to the latest
# N versions of each package, then regenerate the indexes that have them.  The
# repo had grown past 9 GB (every version of every format), exceeding GitHub
# Pages' 1 GB site limit and failing the deploy.
#
# Formats: apt(.deb), rpm(.rpm), alpine(.apk), windows(.msi), macOS(.pkg),
# BSD(.tgz/.txz).  Only apt/rpm/alpine carry an index to regenerate after
# removal; the rest are direct-download, so removal alone suffices.
#
# Pages serves the CURRENT commit's files (not history), so committing the
# pruned tree shrinks the deployed artifact immediately.  This does NOT shrink
# .git (~9.5 GB of old binaries remain in history) — clone size is unchanged
# until history is rewritten separately (git filter-repo / BFG).
#
# Usage:
#   DRY_RUN=1 KEEP=3 ./scripts/prune-package-repo.sh   # show projected result
#   DRY_RUN=0 KEEP=3 ./scripts/prune-package-repo.sh   # apply + regenerate
#
# Regen (DRY_RUN=0, where that format exists): dpkg-scanpackages + apt-ftparchive
# + gzip (apt); createrepo_c (rpm); apk (alpine).

set -uo pipefail

KEEP="${KEEP:-3}"
DRY_RUN="${DRY_RUN:-1}"
VERSION_RE='[0-9]+(\.[0-9]+)+(-[0-9]+)?'
PKG_RE="\.(deb|rpm|apk|msi|pkg|tgz|txz|exe)$"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$ROOT/repo"
[ -d "$REPO" ] || { echo "No repo/ at $REPO"; exit 1; }

REMOVE="$(mktemp)"; trap 'rm -f "$REMOVE"' EXIT
rel() { echo "$1" | sed "s#$REPO/##"; }
# stdin: list → stdout: all but the latest KEEP (oldest first)
to_remove() { local -a a; mapfile -t a < <(sort -V); local n=${#a[@]}
  (( n > KEEP )) && printf '%s\n' "${a[@]:0:n-KEEP}"; return 0; }

[ "$DRY_RUN" = "1" ] && echo "=== DRY RUN (KEEP=$KEEP; DRY_RUN=0 to apply) ===" \
                     || echo "=== PRUNING to latest $KEEP versions ==="
start_bytes=$(du -sb "$REPO" | cut -f1)
echo "Starting repo/ size: $(du -sh "$REPO" | cut -f1)"

# Pass 1 — version-DIRECTORY layouts (immediate children are version dirs that
# hold package files): apt pool/main, server/rpm/centos, the BSD/win/mac dirs.
find "$REPO" -type d | while IFS= read -r d; do
  for sub in "$d"/*/; do
    b=$(basename "$sub" 2>/dev/null) || continue
    if echo "$b" | grep -qE "^${VERSION_RE}$" && ls "$sub"*.* 2>/dev/null | grep -qE "$PKG_RE"; then
      echo "$d"; break
    fi
  done
done | sort -u | while IFS= read -r parent; do
  ls -1 "$parent" 2>/dev/null | grep -E "^${VERSION_RE}$" | to_remove \
    | while IFS= read -r v; do [ -n "$v" ] && echo "$parent/$v" >> "$REMOVE"; done
done

# Pass 2 — FLAT layouts (version-named package files directly in a dir): rpm
# <distro>/<arch>, alpine indexes, etc. Keep latest N per package name.
find "$REPO" -type d | while IFS= read -r d; do
  ls "$d"/*.* 2>/dev/null | grep -qE "$PKG_RE" && echo "$d"
done | while IFS= read -r d; do
  b=$(basename "$d")
  echo "$b" | grep -qE "^${VERSION_RE}$" && continue   # version-dir child (Pass 1)
  for name in $(ls -1 "$d"/*.* 2>/dev/null | grep -E "$PKG_RE" \
                  | xargs -r -n1 basename | sed -E 's/[-_][0-9].*//' | sort -u); do
    ls -1 "$d/$name"[-_][0-9]*.* 2>/dev/null | grep -E "$PKG_RE" | to_remove \
      | while IFS= read -r f; do [ -n "$f" ] && echo "$f" >> "$REMOVE"; done
  done
done

sort -u -o "$REMOVE" "$REMOVE"
count=$(wc -l < "$REMOVE")
removed_bytes=$(du -scb $(cat "$REMOVE") 2>/dev/null | tail -1 | cut -f1)
removed_bytes=${removed_bytes:-0}
projected=$(( (start_bytes - removed_bytes) / 1048576 ))

echo "Marked $count path(s) to remove."
if [ "$DRY_RUN" = "0" ]; then
  xargs -r -d '\n' rm -rf < "$REMOVE"
  # apt
  find "$REPO" -type d -path '*/pool/main' | while IFS= read -r pool; do
    debroot="$(dirname "$(dirname "$pool")")"
    ( cd "$debroot" && mkdir -p dists/stable/main/binary-amd64 \
      && dpkg-scanpackages pool/main /dev/null > dists/stable/main/binary-amd64/Packages \
      && gzip -k -f dists/stable/main/binary-amd64/Packages \
      && ( cd dists/stable && apt-ftparchive release . > Release ) ) && echo "  regen apt: $(rel "$debroot")"
  done
  # rpm
  find "$REPO" -type d -name repodata | while IFS= read -r rd; do d="$(dirname "$rd")"
    if command -v createrepo_c >/dev/null; then ( cd "$d" && createrepo_c . >/dev/null ); echo "  regen rpm: $(rel "$d")"
    else echo "  !! createrepo_c missing — $(rel "$d") repodata STALE"; fi
  done
  # alpine
  find "$REPO" -name 'APKINDEX.tar.gz' | while IFS= read -r idx; do d="$(dirname "$idx")"
    if command -v apk >/dev/null; then ( cd "$d" && apk index -o APKINDEX.tar.gz ./*.apk >/dev/null 2>&1 ); echo "  regen apk: $(rel "$d")"
    else echo "  !! apk missing — $(rel "$d") APKINDEX STALE"; fi
  done
fi

echo ""
echo "Would remove: $((removed_bytes / 1048576)) MB"
echo "Projected repo/ size: ${projected} MB$([ "$DRY_RUN" = 1 ] && echo '  (dry run)')"
[ "$projected" -lt 1024 ] && echo "  ✓ under the 1 GB Pages limit" \
                          || echo "  ✗ still over 1 GB — lower KEEP and re-run"
