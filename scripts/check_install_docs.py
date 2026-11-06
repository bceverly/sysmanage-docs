#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Keep the installation instructions true.

The 2026-11-05 audit found install guidance that could not work or was
unsafe: curl-to-bash from hosts that do not resolve, Docker and Kubernetes
recipes for images that were never published, APT sources with
``trusted=yes``, RPM repos with ``gpgcheck=0``, and five different ports.
This check fails on each of those patterns anywhere in the published pages
or the README, so they cannot creep back.

``--online`` also asks repo.sysmanage.org for every repository file the
pages name (keyrings, latest.txt, the RPM key) and fails on a 404.  It
needs the network, so ``make lint`` runs the offline part only.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"node_modules", "screenshots", "scripts", "Presentations", "SignPath", "repo", "_site"}

# (pattern, why) -- each matched against page text with tags kept, so a
# command in <pre><code> and prose both count.
FORBIDDEN = [
    (r"curl[^\n|<]*\|\s*(sudo\s+)?(ba)?sh\b", "curl piped to a shell -- install the signed packages instead"),
    (r"wget[^\n|<]*\|\s*(sudo\s+)?(ba)?sh\b", "wget piped to a shell -- install the signed packages instead"),
    (r"install\.sysmanage\.(org|com)", "install.sysmanage.* does not exist"),
    (r"releases\.sysmanage\.org", "releases.sysmanage.org does not exist; use repo.sysmanage.org"),
    (r"\[\s*trusted=yes\s*\]", "trusted=yes disables APT signature checks"),
    (r"gpgcheck\s*=\s*0", "gpgcheck=0 disables RPM signature checks"),
    (r"--nogpgcheck", "--nogpgcheck disables RPM signature checks"),
    (r"--allow-unauthenticated", "--allow-unauthenticated disables APT signature checks"),
    (r"\bsysmanage(/agent)?:latest\b", "no SysManage container image is published"),
    (r"docker run[^\n<]*sysmanage", "no SysManage container image is published"),
    (r":(8443|8444|6443)\b", "the server is reached on 443 only"),
    (r"/etc/sysmanage-agent/config\.toml", "the agent's config is /etc/sysmanage-agent.yaml"),
    (r"/opt/sysmanage/(config|ssl)\b", "no such path: config is /etc/sysmanage.yaml, TLS /etc/sysmanage/tls"),
]

# Lines that discuss a forbidden pattern on purpose (a warning not to use it).
ALLOWED_CONTEXT = re.compile(r"(never|do not|don't|not use|instead of|warning|refus|disables)", re.I)

REPO_URL = re.compile(r"https://repo\.sysmanage\.org/[A-Za-z0-9_./-]+\.(gpg|txt|asc|repo|flatpakrepo)|https://repo\.sysmanage\.org/agent/rpm/RPM-GPG-KEY-sysmanage")


def published_files() -> list[Path]:
    files = [REPO / "README.md"]
    for path in sorted(REPO.rglob("*.html")):
        if not SKIP_DIRS.intersection(path.relative_to(REPO).parts):
            files.append(path)
    return files


def offline_problems() -> list[str]:
    problems = []
    for path in published_files():
        lines = path.read_text(encoding="utf-8").splitlines()
        for number, line in enumerate(lines, 1):
            # A warning against a pattern may finish on the next line.
            context = " ".join(lines[max(0, number - 2):number + 1])
            for pattern, why in FORBIDDEN:
                if re.search(pattern, line) and not ALLOWED_CONTEXT.search(context):
                    problems.append(f"{path.relative_to(REPO)}:{number}: {why}")
    return problems


def online_problems() -> list[str]:
    urls = set()
    for path in published_files():
        urls.update(m.group(0) for m in REPO_URL.finditer(path.read_text(encoding="utf-8")))
    problems = []
    for url in sorted(urls):
        # GET with an ordinary user agent: the CDN in front of the repository
        # answers 403 to urllib's default agent.
        request = urllib.request.Request(url, headers={"User-Agent": "curl/8.5.0"})
        try:
            # nosemgrep: dynamic-urllib-use-detected -- fixed https host from our own pages
            with urllib.request.urlopen(request, timeout=20):  # nosec B310
                pass
        except urllib.error.HTTPError as error:
            problems.append(f"{url}: HTTP {error.code}")
        except (urllib.error.URLError, OSError) as error:
            problems.append(f"{url}: {error}")
    print(f"checked {len(urls)} repository URL(s)")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--online", action="store_true", help="also fetch every repository URL")
    args = parser.parse_args()
    problems = offline_problems() + (online_problems() if args.online else [])
    if problems:
        print("ERROR: installation instructions that would mislead a reader:")
        for line in problems:
            print(f"  {line}")
        return 1
    print("[OK] installation instructions: no unsafe or impossible commands")
    return 0


if __name__ == "__main__":
    sys.exit(main())
