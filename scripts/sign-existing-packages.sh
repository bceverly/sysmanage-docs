#!/usr/bin/env bash
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.
#
# ONE-TIME: sign packages that were published before signing existed.
#
# WHY THIS IS SEPARATE FROM THE PRUNE JOB
# ---------------------------------------
# The obvious place for this was prune-package-repo.sh, which already pulls the
# whole repo and holds the key.  It is the wrong place.  That job mirrors
# package files back with ``--size-only``, and re-signing an rpm changes its
# BYTES while usually keeping the same SIZE -- so the upload would be skipped
# while the regenerated repodata carried the new checksums, and dnf would report
#
#   package does not match intended download
#
# ...for every package it touched.  A recurring job that mutates packages is
# also a standing risk: it re-signs on a weekly cron forever, for no benefit
# after the first pass.
#
# So this is a deliberate, one-shot operation with a FULL-CONTENT sync back.
#
# WHAT IT DOES
#   1. pull repo/ from R2
#   2. sign every rpm that is not already signed (idempotent: signed ones skip)
#   3. regenerate apt + rpm metadata so indices match the new bytes
#   4. sync back WITHOUT --size-only, so changed content always uploads
#
# After this has run once, packages are signed at BUILD time by the release
# workflows and this script should not be needed again.
#
# Required env: APT_SIGNING_KEY_ID (with or without a trailing '!'),
#               a gpg keyring holding that key, and R2 credentials.
#   APT_GPG_EXTRA  optional loopback/passphrase args for non-interactive use.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$ROOT/repo"
[ -d "$REPO" ] || { echo "ERROR: no repo/ at $REPO — pull from R2 first" >&2; exit 1; }

KEY="${APT_SIGNING_KEY_ID:-}"
[ -n "$KEY" ] || { echo "ERROR: APT_SIGNING_KEY_ID is not set" >&2; exit 1; }
KEY_NOBANG="${KEY%!}"

command -v rpmsign >/dev/null 2>&1 || {
    echo "ERROR: rpmsign not found (install the 'rpm' package)" >&2
    exit 1
}

signed=0
skipped=0
failed=0

while IFS= read -r rpmfile; do
    [ -n "$rpmfile" ] || continue
    # Bias towards signing.  A false "already signed" verdict leaves a package
    # unverifiable, which breaks gpgcheck=1 for a real user; a false "unsigned"
    # verdict just re-signs something harmlessly (--addsign replaces).  So skip
    # ONLY when a signature is positively identified.
    sig="$(rpm -qp --qf '%{SIGPGP}%{SIGGPG}%{RSAHEADER}%{DSAHEADER}' "$rpmfile" 2>/dev/null || true)"
    case "$sig" in
        ""|*"(none)(none)(none)(none)"*) ;;   # unsigned -> fall through and sign
        *) skipped=$((skipped + 1)); continue ;;
    esac

    # shellcheck disable=SC2086
    if rpmsign --addsign \
        --define "_gpg_name $KEY_NOBANG" \
        --define "__gpg_sign_cmd %{__gpg} gpg --batch --no-verbose --no-armor ${APT_GPG_EXTRA:-} --no-secmem-warning -u $KEY_NOBANG -sbo %{__signature_filename} %{__plaintext_filename}" \
        "$rpmfile" >/dev/null 2>&1
    then
        signed=$((signed + 1))
    else
        echo "ERROR: rpmsign failed for ${rpmfile#"$REPO"/}" >&2
        failed=$((failed + 1))
    fi
done < <(find "$REPO" -name '*.rpm')

echo "rpm signing: $signed newly signed, $skipped already signed, $failed failed"
[ "$failed" -eq 0 ] || exit 1

# Indices must be regenerated AFTER signing: the signature changes each
# package's checksum, and metadata describing the pre-signature bytes would
# fail verification just as surely as no signature at all.
while IFS= read -r debroot; do
    "$ROOT/scripts/build-apt-repo.sh" "$debroot"
done < <(find "$REPO" -type d -path '*/deb')

if command -v createrepo_c >/dev/null 2>&1; then
    while IFS= read -r rd; do
        d="$(dirname "$rd")"
        ( cd "$d" && createrepo_c --update . >/dev/null )
        echo "  regen rpm: ${d#"$REPO"/}"
    done < <(find "$REPO" -type d -name repodata)
else
    echo "ERROR: createrepo_c missing — rpm indices would describe pre-signature bytes" >&2
    exit 1
fi

echo
echo "Signing pass complete.  Sync back WITHOUT --size-only:"
echo "  aws s3 sync repo/ s3://\$R2_BUCKET/ --delete   # content compare, not size"
