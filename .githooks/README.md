# Git hooks

This directory holds the project's shareable git hooks. They're
activated by pointing `core.hooksPath` at this directory (instead of
the default `.git/hooks/` which is not version-controlled), matching the
sysmanage, sysmanage-agent, and sysmanage-professional-plus repos.

## Installation

Run `make install-hooks` from the repo root once after cloning. It
sets `core.hooksPath = .githooks` for this clone — idempotent, safe to
re-run. `make install-dev` runs `make install-hooks` automatically as
its last step, so for most contributors there's nothing to do beyond
the normal setup workflow.

## Active hooks

### `pre-push`

Runs `make lint` before allowing a push to remote. If linting fails,
the push is blocked with an error pointing at the failing tool. For
this docs repo, `make lint` covers file-length, pylint, security
(bandit), eslint, and the i18n gates — key existence (`i18n-validate`)
and untranslated-string detection (`translate-check`) — so this one
hook enforces every local gate CI would. In a genuine emergency the
hook can be bypassed with `git push --no-verify`, but the next CI run
will fail the same way so the bypass only delays the fix.

> Note: the older `scripts/hooks/pre-push` (a tag-only `translate-check`
> guard) is superseded by this hook — `make lint` already runs
> `translate-check` on every push.
