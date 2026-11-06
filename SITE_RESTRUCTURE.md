# Website and documentation restructure (started 2026-11-05)

Goal: the marketing site sells the operational outcome; the documentation
proves the technical claims. Believe -> Evaluate -> Trust, with the biggest
investment in the middle step: a reproducible first experience of managing a
mixed fleet.

Source: external review (2026-11-05) plus four audits of this repo and the
code (installation guidance, claims and numbers, edition/platform matrix,
docs inventory). Decisions (Bryan, 2026-11-05):

- Fictional architecture pages are retired and merged into a few accurate
  ones; old URLs point at the replacements.
- Where the site and the code disagree on editions, the code
  (`sysmanage/backend/licensing/features.py`) is the truth.
- Enterprise SaaS is "hosted on request".
- Priority Support, SLA Guarantee, "in production" and "Most Popular" stay as
  offered commercial terms.

Rules for every item: facts come from the code, the release workflows or
ROADMAP measurements, never from memory; every new string goes into all 14
locales and is verified (`make translate` + `make i18n-verify`); screenshots
come from `make screenshots`; American spelling; ASCII hyphens.

## Week 1 -- Trust and consistency

- [x] **One install path.** Native signed packages are the recommended path on
  every page (README, getting-started, quick-start, first-deployment,
  server/deployment, agent/deployment, agent-approval, tutorials). Remove the
  curl-to-bash commands (install.sysmanage.org / .com do not resolve), the
  Docker / Kubernetes / compose deployments (no image or Dockerfile exists),
  `releases.sysmanage.org`, Chocolatey. One port story (agents reach the
  server on 443 through nginx), one agent config path
  (`/etc/sysmanage-agent.yaml`), one Python range, OS release lists taken from
  the release workflows.
- [x] **Signed everywhere it can be; honest where it cannot.** Show the APT key
  fingerprint; say plainly which downloads are checksum-only (Alpine, BSD
  direct downloads, macOS .pkg) instead of implying signatures.
- [x] **Code-repo READMEs.** `sysmanage-agent/README.md` (`trusted=yes`,
  `gpgcheck=0`, dead el8 / fedora/39 paths) and `sysmanage/README.md` (leads
  with a from-source quick start) match the docs.
- [x] **Numbers with a source, or no number.** Replace invented metrics
  (system-architecture, performance-stability, message-flow,
  performance-testing, design-principles, system-overview, sizing advice that
  contradicts scaling.html) with the Phase 22 measurements and a methodology
  note; real test counts and coverage; remove "100% coverage", "0% flaky".
- [x] **No certifications we do not hold.** Remove HSM / FIPS 140-2 Level 3/4,
  "supported frameworks" SOC 2 / FedRAMP / ISO 27001 / PCI / HIPAA / GDPR,
  "compliance certification"; keep "FIPS-aware" wording.
- [x] **No features we do not ship.** Multi-server HA / load balancing (Phase
  34), integrations that do not exist (Puppet node classifier, AWS SSM,
  Terraform, SMS), DragonFly BSD, apk/scoop package management.
- [x] **Retire the fictional architecture pages** and merge into accurate
  pages: performance-metrics, performance-optimization, performance-stability,
  load-balancing, queue-management, data-synchronization, retry-logic,
  migration-strategy, system-overview/system-architecture,
  scaling-strategies. Old URLs become short pages that point at the new ones.
- [x] **Editions match the code.** One edition data source drives the
  homepage cards, the Pro+ index and the Enterprise SaaS page; fix every
  conflict found by the audit (vuln/compliance/secrets = Professional; MFA and
  RBAC = Community; reporting = Professional; host metrics and NTP policy =
  Enterprise; Community has firewall *status*, not firewall management;
  remove "Advanced RBAC"; Enterprise SaaS "hosted on request").
- [x] **Softer, defensible positioning.** "Consolidate fragmented fleet
  operations" instead of wholesale replacement; remove absolutes the code
  contradicts ("works the same way on every OS", "structurally impossible",
  "most secure platform available", "military-grade").
- [x] **BSD everywhere it belongs** in platform lists.
- [x] **Every docs page has the site shell** (42 pages load no scripts: no
  header, footer or translation).
- [x] **Stale facts:** EOL OS releases, "Phase N" pages and headings, old
  version references, the Windows 10 diagram, British spellings.
  British spellings: none in prose ("cancelled" is the product's status
  value). EOL releases: only in cited competitor facts and sample output.
  Supported-platforms page gained the release x architecture x install
  method table (`releases` in data/capabilities.yaml). "Phase N" removed
  from every title and heading (file names kept, so links hold). The
  architecture diagram claimed mTLS, CentOS, Windows 10 and macOS 10.15;
  it now says TLS and names what is packaged.
- [ ] **"Phase" in body text (after the translation run; sysmanage ROADMAP
  25.6):** phases are an internal planning term (Bryan, 2026-11-05) and
  ten pages still cite them in prose -- roadmap/index.html, five
  architecture pages, server/deployment, server/troubleshooting,
  deployment/production-checklist, getting-started/first-deployment
  ("Phase 34" for HA, "Phase 29", "ROADMAP 27.3"). Name the feature or say
  "planned", update the strings in 14 locales, and add a lint check that
  fails on "Phase <number>" / "ROADMAP <number>" in published pages.

## Week 2 -- The evaluation journey

- [x] **Supported platforms matrix** (docs): OS x release x architecture x
  install method, and capability x OS (Yes / Partial, with what is missing /
  No), generated from one data file.
- [x] **Editions and availability** (docs + marketing): capability x edition x
  status (Available with the version that shipped it / In development /
  Planned with its phase).
- [x] **"Your first mixed fleet in 30 minutes"** tutorial: Community server on
  Ubuntu, agents on Ubuntu and FreeBSD (Windows as the alternative), approve,
  unified inventory, updates on both, one safe operation, its result and audit
  record. Exact commands, expected output, recovery for common errors. Run end
  to end on fresh VMs before publishing.
- [x] **/evaluate/** marketing page: what the evaluator needs, how long it
  takes, what Community includes, what success looks like, a note an
  infrastructure director can forward to an engineer, and the commercial
  evaluation path.

## Week 3 -- Simpler marketing

- [x] **Homepage in six steps:** problem, Monday 9:04, outcome, proof (short
  real-product walkthrough), buyer journeys, next action (Try Community /
  Evaluate for my organization / Talk to us about MSP or Enterprise SaaS).
- [x] **Detail moves to its own pages:** /platform/ (capabilities, BSD,
  packages), /pricing/ (editions with availability), /compare/ (by product).
- [x] **Buyer journeys:** infrastructure operations, security and compliance,
  MSPs -- each with its problem, an example workflow and an evaluation CTA.
- [x] **Comparison by product and use case** (Ansible, Puppet, Salt, Chef,
  Satellite, Landscape, Intune, Jamf, SCCM/MECM), each cell cited to vendor
  documentation with the date checked.
- [ ] **Product walkthrough:** a short captioned sequence of real screenshots
  across Windows, Linux and BSD hosts, reproducible with `make screenshots`.
- [ ] **Believable screenshot data:** the seed shows `apt` on the RHEL host,
  packages named `sec-pkg-0`, the screenshot VM itself (`sysmanage-shots`,
  version "unknown", Approval Needed) in the hosts list, a host with no
  platform, and macOS as "Darwin". Real package names per OS, the right
  package manager per host, the VM hidden or approved, then `make
  screenshots`.

## Week 4 -- Docs usability

- [x] **Docs landing by task:** Evaluate, Deploy in production, Operate your
  fleet, Security & trust, Integrate & extend, Architecture & development.
- [x] **Search:** a client-side index built by a make target, with a gate that
  fails when the index is stale.
- [x] **Version information:** every docs page says which release it
  describes; a release notes page.
- [x] **Production guides:** upgrade, rollback, server disaster recovery
  (database, OpenBAO, sysmanage.yaml, certificates, license), a
  production-readiness checklist; rewrite administration/backup.html.
- [x] **Runbooks:** patch a critical CVE across the fleet, onboard 100 hosts,
  rotate certificates, replace a failed server.
- [x] **API examples** in Python, Bash and PowerShell for common tasks; API
  tokens linked from the API docs.
- [ ] **Docs that stay true:** a gate that checks install commands against
  the published repositories and keys, and a release-gated review of the
  support matrix.

## Found along the way (code, not the site)

Found by running the 30-minute evaluation on fresh Ubuntu 24.04 and FreeBSD
14.5 VMs (2026-11-05); FIXED in the working trees (server + agent), proven on
the VMs, tests added -- they ship with the next release (3.12.1.7):

- [x] nginx would not start on Ubuntu 24.04/22.04, Debian 12, RHEL 9:
  `http2 on;` needs nginx 1.25.1 (template now uses `listen 443 ssl http2`).
- [x] `/etc/sysmanage/tls/` did not exist after install (deb postinst creates it).
- [x] Ubuntu's stock nginx site answered port 80 ("Welcome to nginx!") (deb
  postinst disables the untouched stock link).
- [x] The recovery admin could not approve hosts ("User not found") and the
  Users page needed SMTP: new first-run "Create your administrator" form
  (POST /api/v1/security/first-admin) offered by the banner.
- [x] The banner told fresh installs to regenerate secrets the installer had
  already generated (now shows only the steps that apply).
- [x] The FreeBSD agent package installed 0 bytes (no files section),
  depended on py311 packages FreeBSD no longer builds, lacked 5 runtime
  modules, created the wrong account, never created /etc/sysmanage-agent,
  and its rc status/stop could not see the agent (new
  installer/freebsd/build_pkg_manifest.py + post-install.sh, rc -P, PATH).
- [x] Package install from the Install dialog: "auto" meant apt everywhere;
  `sudo DEBIAN_FRONTEND=...` refused without SETENV (env_keep now); FreeBSD
  sudoers did not cover /usr/local/sbin/pkg; completion messages lost their
  fields (server parser now tolerant, agent sends `data`) so installs stayed
  "in progress" forever; host search was fleet-wide and buried exact matches.
- [x] Host approval was audited only as "Updated host" (now "Approved host").
- [x] Agent Recommends pulled virtinst/qemu/GTK onto every Ubuntu/RPM host
  (now Suggests -- Bryan, 2026-11-05).
- [x] The server's FreeBSD package: same no-files / py311 / relative-path
  defects as the agent's, plus: pip-built venv (compiling pydantic-core),
  nginx config with literal `%%PREFIX%%` tokens and a wrong frontend root,
  never included by FreeBSD's stock nginx.conf, no TLS directory; rc ran
  from / (backend not importable, `logs/` unwritable) and migrated with a
  bare `alembic upgrade head`; OpenBAO rc set `openbao_user` (daemon could
  not open its log) and called python3.11; post-install started OpenBAO,
  which pkg reaps; `sysmanage-migrate` missing and unable to read the
  root:wheel config. Fixed with `installer/freebsd/build_pkg_manifest.py`
  (deps read from the port's RUN_DEPENDS, which gained regex + packaging)
  and proven end to end on FreeBSD 14.5: install, migrate, OpenBAO
  unsealed, HTTPS console and /api/health through nginx, 80 -> 301.
- [ ] FreeBSD install reports installed_version None (cosmetic).
- [ ] RHEL/openSUSE nginx default server may also answer port 80 (check).
- [x] **RPM removal wipes the server's identity:** `dnf remove` / `zypper
  remove` run `rm -rf /etc/sysmanage /var/lib/sysmanage` (CA, TLS key,
  OpenBAO token) -- `installer/centos/sysmanage.spec:410-420`,
  `installer/opensuse/sysmanage.spec:382-396`; Debian does it only on purge.
- [x] `scripts/sysmanage-migrate` and `installer/ubuntu/sysmanage.service`
  export `SYSMANAGE_CONFIG`; `backend/config/config.py` reads
  `SYSMANAGE_CONFIG_PATH`, so the wrapper's /usr/local/etc and /usr/pkg/etc
  search does nothing.
- [x] FreeBSD server: the package writes `/usr/local/etc/sysmanage/config.yaml`
  but the server reads `/etc/sysmanage.yaml` (rc.d never sets the path).
- [ ] Windows: OpenBAO init/unseal runs only at MSI install, nothing unseals
  at boot (unverified at runtime).
- [ ] Package rollback: `migration_compat.is_at_or_above` refuses engines
  when the database is at a revision the older code does not know.
- [ ] Containers: `container_engine` is Professional but child-host listing
  needs the Enterprise child_host_handlers engine; decide which is right and
  align `data/capabilities.yaml` (`child_hosts`).
- [ ] ROADMAP 25.9: unseal keys live in `/var/lib/openbao/init.json` on
  package installs (the YAML only via the secure-installation script).

- [ ] Update apply has no zypper, pacman or pkgin handler (detected, never
  applied): `sysmanage-agent/src/sysmanage_agent/collection/update_detection_linux.py:360-370`,
  `update_detection_bsd.py:852-869`.
- [x] Audit-log export never worked (`/{audit_id}` declared before
  `/export`); fixed, proven on the eval VM.
- [x] Community had no menu entry for its own audit log (Reports needs the
  Professional reporting engine); Security > Audit Log added.
- [x] RPM removal no longer deletes /etc/sysmanage and /var/lib/sysmanage.
- [x] `SYSMANAGE_CONFIG` now honored by the server; FreeBSD server rc exports
  its config path; its "database configured" check no longer passes on a
  comment.
- [ ] Update execution log endpoint reads columns UpdateExecutionLog lacks
  (`status`, `success`, `error_message`) -- 500 for any host with rows.
- [ ] Enterprise Update Profiles "Trigger Now" sends apply_updates with no
  packages; the agent answers "No packages specified".
- [ ] Reports menu needs the `reports` feature, which TIER_FEATURES grants
  only to Enterprise, while reporting_engine is Professional.
- [ ] /api/v1/updates/results and /update-status shadowed by /{host_id}.
- [ ] Agent config templates carry server.reconnect_interval /
  max_reconnect_attempts, which the agent never reads.
- [ ] Advisory engine fetches only Ubuntu USN and OpenBSD errata; RHSA,
  SUSE-SU, DSA and FreeBSD-SA are recognized but skipped.
- [ ] Child-host listing needs the Enterprise-only child_host_handlers_engine
  while its message says Professional+ (`sysmanage/backend/api/handlers/child_host/listing.py:41-52`).
- [ ] Upgrade profiles return 402 without the Enterprise automation engine,
  but Phase 26.1 makes automatic updates Community.
- [ ] ROADMAP "Current Version: v3.10.0.0" is stale.
