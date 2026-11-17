#!/bin/sh
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.
#
# Pipe seed files into a command on the screenshot VM, indent what it prints,
# and FAIL when it fails.
#
#   vm_seed.sh [--soft] <label> <make target> <remote command> <file>...
#
# Each seed used to run as `cat seed.py | vagrant ssh -c ... | sed ... || echo
# warning`.  sed always succeeds, so the warning never printed: a seed that
# crashed went unnoticed until a screenshot came out empty or wrong, much
# later in the run.  This keeps the live, indented output but takes the exit
# status from vagrant ssh (which passes on the remote command's), and stops
# the run on a failure.  --soft is for a step that is genuinely optional: it
# says the step was skipped and carries on.
#
# The Makefile passes its colors in RED, YELLOW and RESET (empty when the
# terminal has none).  POSIX sh, so it also runs under Git Bash on Windows.

soft=
if [ "$1" = "--soft" ]; then
    soft=1
    shift
fi
if [ $# -lt 4 ]; then
    echo "usage: vm_seed.sh [--soft] <label> <make target> <remote command> <file>..." >&2
    exit 2
fi
label=$1
target=$2
remote=$3
shift 3

status=$(mktemp) || exit 1
trap 'rm -f "$status"' EXIT

{
    cat "$@" | vagrant ssh -c "$remote" 2>/dev/null
    echo $? > "$status"
} | sed 's/^/  /'
rc=$(cat "$status")

[ "$rc" = 0 ] && exit 0

if [ -n "$soft" ]; then
    printf '%s%s skipped (exit %s); carrying on without it.%s\n' \
        "$YELLOW" "$label" "$rc" "$RESET"
    exit 0
fi

case "$1" in
    /*) seed=$1 ;;
    *) seed=sysmanage-docs/screenshots/$1 ;;
esac
printf '%s[FAIL] %s failed (exit %s).%s\n' "$RED" "$label" "$rc" "$RESET"
printf '%s\n' \
    "  Its error is printed just above.  The screenshots that use this data" \
    "  would come out empty or wrong, so the run stops here.  This is a" \
    "  problem in the seed or the VM, not in the product's own tests." \
    "  To fix it:" \
    "    1. Read the error above; the seed is $seed." \
    "    2. Fix the seed (or the VM state it names)." \
    "    3. Rerun just this step against the running VM: make $target" \
    "       then finish with the capture target you were running."
exit "$rc"
