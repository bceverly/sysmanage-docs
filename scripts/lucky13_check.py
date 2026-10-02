#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""MITRE "Lucky 13" unforgivable vulnerabilities -- the sysmanage-docs checks.

Steve Christey (MITRE), "Unforgivable Vulnerabilities", Black Hat USA 2007
(https://cwe.mitre.org/documents/unforgivable_vulns/unforgivable.pdf):
thirteen weakness classes so well documented, obvious and cheap to find that
shipping one is unforgivable.  Every SysManage repository checks the ones that
apply to it; this is the documentation site's share.

WHAT THIS REPOSITORY CHECKS
  #2  XSS (CWE-79): no raw-HTML sinks (innerHTML, outerHTML,
      insertAdjacentHTML, document.write, eval, new Function) in the site's
      JavaScript or inline scripts except reviewed ones; and every
      translation in assets/locales/*.json uses only the markup our own
      strings use -- translations are machine-generated and rendered as HTML,
      so a stray tag is an injection (assets/js/i18n.js sanitizes at render
      time with the same allow-list; this keeps the files clean too).
  #4  remote file inclusion (CWE-98): no third-party <script src> without a
      Subresource Integrity hash; no eval/exec/dynamic import in our scripts.
  #6  world-writable files (CWE-276): no chmod granting "others" write in
      scripts, the Makefile, hooks or workflows.
  #9  grow-your-own crypto (CWE-327): no MD5/SHA-1 for security, no
      PyCrypto, DES, RC4, ECB or rot13 in our Python.
  #11 symlink following (CWE-61): no tempfile.mktemp and no fixed /tmp paths
      (shell `mktemp` is fine -- it creates the file securely).
  #12 hard-coded / default passwords (CWE-259): no private keys, cloud or
      GitHub tokens, or password/secret literals in scripts, tooling,
      workflows or the Makefile (the docs pages' own example configs use
      placeholders and are not credentials; GPG PUBLIC keys are fine).

WHAT DOES NOT APPLY HERE
  #1 buffer overflow, #3 directory traversal, #5 SQL injection, #7 direct
  request, #8 authenticated=1, #10 privilege escalation via Help and #13
  integer overflow need a server, a database or privileged code; this is a
  static site served as files.  The server, agent and Professional+
  repositories check those.

A hit is fixed, or added to ALLOWED with the reason it is safe -- the
allow-list is the reviewed record.  Exit status 1 on any unreviewed hit.

Usage:  python3 scripts/lucky13_check.py      (make test-lucky13)
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"node_modules", ".git", "__pycache__", "SignPath", "htmlcov", ".venv", "venv"}
SELF = "scripts/lucky13_check.py"  # its own patterns would match

# (check, repo-relative path, text found on the line) -> why it is safe.
ALLOWED = {
    ("2", "assets/js/navbar.js", "existingHeader.outerHTML"): (
        "inserts buildNavigation(): a static template from the navConfig "
        "object in this file; no request or translation data"
    ),
    ("2", "assets/js/navbar.js", "insertAdjacentHTML('afterbegin', buildNavigation())"): (
        "same static navigation template"
    ),
    ("2", "assets/js/components.js", "tempDiv.innerHTML = headerHTML"): (
        "static header template; ${root} is the site root computed from this "
        "script's own URL"
    ),
    ("2", "assets/js/components.js", "tempDiv.innerHTML = footerHTML"): (
        "static footer template, as above"
    ),
    ("2", "assets/js/main.js", "button.innerHTML = '"): "a fixed glyph literal",
    ("2", "assets/js/main.js", "icon.innerHTML = '"): "a fixed glyph literal",
    ("2", "assets/js/main.js", "scrollToTopButton.innerHTML = '"): "a fixed glyph literal",
    ("2", "assets/js/i18n.js", "button.innerHTML = `<span class=\"language-icon\">"): (
        "language names from the static table in this file"
    ),
    ("2", "assets/js/i18n.js", "option.innerHTML = `"): (
        "language names and codes from the static table in this file"
    ),
    ("2", "assets/js/i18n.js", "template.innerHTML = html"): (
        "the sanitizer itself: parses into an inert <template> (nothing loads "
        "or runs there) and returns only allow-listed nodes"
    ),
    ("11", "screenshots/seed_malware.py", '"/tmp/.cache/kworker.json"'): (
        "demo data: the path a seeded malware finding reports; never opened"
    ),
    ("12", "screenshots/provision/provision.sh", "jwt_secret: \"dev-screenshot-secret-not-for-production\""): (
        "throwaway screenshot VM built and destroyed by make screenshots; "
        "never a real deployment"
    ),
}

# The markup our translations may carry (mirrors I18n.sanitizeHtml).
ALLOWED_TAGS = {"a", "b", "br", "code", "div", "em", "i", "kbd", "li", "ol", "p",
                "pre", "small", "span", "strong", "sub", "sup", "ul"}  # fmt: skip
ALLOWED_ATTRS = {"href", "class", "target", "rel", "title"}

PY = {".py"}
SHELLISH = {".sh", ".yml", ".yaml", "Makefile", "pre-push", "pre-commit"}


def _files(roots, suffixes):
    for root in roots:
        base = REPO / root
        if not base.exists():
            continue
        for path in [base] if base.is_file() else sorted(base.rglob("*")):
            if not path.is_file() or SKIP_DIRS & set(path.relative_to(REPO).parts):
                continue
            if path.suffix in suffixes or path.name in suffixes:
                yield path


def _scan(check, roots, suffixes, pattern, line_ok=None):
    regex = re.compile(pattern)
    hits = []
    for path in _files(roots, suffixes):
        rel = str(path.relative_to(REPO))
        if rel == SELF:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(lines, 1):
            if not regex.search(line) or (line_ok and line_ok(line)):
                continue
            if any(c == check and p == rel and frag in line for c, p, frag in ALLOWED):
                continue
            hits.append(f"{rel}:{number}: {line.strip()[:110]}")
    return hits


def check_2_html_sinks():
    # The site as served: its JavaScript and its pages' inline scripts.
    sinks = (r"\.(inner|outer)HTML\s*=|insertAdjacentHTML|document\.write\("
             r"|(?<![\w$.])eval\(|new Function\(")  # fmt: skip
    return _scan("2", ["assets/js"], {".js"}, sinks) + _scan("2", ["."], {".html"}, sinks)


def _strings(value, path=""):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _strings(child, f"{path}.{key}" if path else key)
    elif isinstance(value, str):
        yield path, value


TAG = re.compile(r"<\s*(/?)\s*([a-zA-Z][\w:-]*)([^>]*)>")
ATTR = re.compile(r"([^\s=/]+)\s*(?:=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+))?")


def check_2_locale_markup():
    hits = []
    for path in sorted((REPO / "assets/locales").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for key, text in _strings(data):
            for match in TAG.finditer(text):
                tag = match.group(2).lower()
                if tag not in ALLOWED_TAGS:
                    hits.append(f"{path.name}: {key}: tag <{tag}>")
                    continue
                for attr in ATTR.finditer(match.group(3)):
                    name = attr.group(1).lower()
                    value = (attr.group(2) or "").strip("\"'").strip()
                    if name not in ALLOWED_ATTRS:
                        hits.append(f"{path.name}: {key}: <{tag} {name}=...>")
                    elif name == "href" and re.match(r"[a-z][a-z0-9+.-]*:", value, re.I) \
                            and not re.match(r"(https?|mailto):", value, re.I):  # fmt: skip
                        hits.append(f"{path.name}: {key}: href {value[:40]}")
    return hits


def check_4_remote_code():
    hits = []
    script = re.compile(r"<script\b[^>]*\bsrc\s*=\s*[\"'](https?:)?//", re.I)
    for path in _files(["."], {".html"}):
        rel = str(path.relative_to(REPO))
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if script.search(line) and "integrity=" not in line:
                hits.append(f"{rel}:{number}: third-party <script> without integrity=")
    return hits + _scan("4", ["scripts", "screenshots", "add_test_user.py"], PY,
                        r"(^|[^.\w])(eval|exec)\(|__import__\(|import_module\(")  # fmt: skip


def check_6_world_writable():
    octal = r"[0-7]?[0-7][0-7][2367]\b"
    return _scan("6", ["scripts", "screenshots", ".github", ".githooks", "Makefile"],
                 SHELLISH | PY,
                 rf"chmod\s+(-\w+\s+)*{octal}|chmod\s+(-\w+\s+)*[ugoa]*[oa][ugoa]*\+[rxX]*w"
                 rf"|0o{octal}|S_IWOTH|umask\s*\(?0+\)?\s*$")  # fmt: skip


def check_9_crypto():
    return _scan("9", ["scripts", "screenshots", "add_test_user.py"], PY,
                 r"hashlib\.(md5|sha1)\(|hashlib\.new\(['\"](md5|sha1)|\bfrom Crypto\b"
                 r"|\bimport Crypto\b|\bARC4\b|TripleDES|modes\.ECB|rot13",
                 line_ok=lambda line: "usedforsecurity=False" in line)  # fmt: skip


def check_11_tmp():
    return _scan("11", ["scripts", "screenshots", "add_test_user.py", ".github", "Makefile"],
                 SHELLISH | PY, r"tempfile\.mktemp\(|[\"'\s=]/(var/)?tmp/[\w.-]+")  # fmt: skip


def check_12_credentials():
    pattern = (
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----|AKIA[0-9A-Z]{16}|ghp_[0-9A-Za-z]{30,}"
        r"|github_pat_[0-9A-Za-z_]{20,}|xox[abp]-[0-9A-Za-z-]{10,}|sk-[A-Za-z0-9]{32,}"
        r"|(password|passwd|secret|token|api_key)\w*\s*[:=]\s*[\"'][^\"'$%{<\s]{6,}[\"']"
    )
    roots = ["scripts", "screenshots", ".github", "Makefile", "add_test_user.py",
             "screenshot-generator.js", "real-screenshot.js", "_config.yml"]  # fmt: skip
    return _scan("12", roots, SHELLISH | PY | {".js", ".mjs", ".json", ".conf"}, pattern,
                 line_ok=lambda line: "secrets." in line)  # fmt: skip


CHECKS = [
    ("#2 XSS (CWE-79): raw HTML sinks", check_2_html_sinks),
    ("#2 XSS (CWE-79): markup in translations", check_2_locale_markup),
    ("#4 remote file inclusion (CWE-98)", check_4_remote_code),
    ("#6 world-writable files (CWE-276)", check_6_world_writable),
    ("#9 grow-your-own crypto (CWE-327)", check_9_crypto),
    ("#11 symlink following (CWE-61)", check_11_tmp),
    ("#12 hard-coded passwords (CWE-259)", check_12_credentials),
]


def main() -> int:
    failed = 0
    for title, check in CHECKS:
        hits = check()
        if hits:
            failed += 1
            print(f"FAIL  {title}")
            for hit in hits:
                print(f"      {hit}")
        else:
            print(f"ok    {title}")
    print("n/a   #1 #3 #5 #7 #8 #10 #13: no server, database or privileged code "
          "in this repository (checked in sysmanage, sysmanage-agent, Professional+)")  # fmt: skip
    if failed:
        print("\nFix each hit, or add it to ALLOWED in scripts/lucky13_check.py with "
              "the reason it is safe.")  # fmt: skip
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
