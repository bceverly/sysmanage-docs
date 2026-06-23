# SysManage Documentation Audit

A micro-level cross-reference of every UI surface (page, tab, button, dialog,
report, menu item) against the documentation under `docs/`. Goal: identify
every genuine gap so we can close them one at a time.

**Regenerated 2026-06-22** (supersedes the 2026-05-02 inventory, which went stale
after a large fill-pass — 118 of 120 doc pages changed in the interim, and every
priority gap it listed had since been closed). This pass enumerates each page's
surface from the actual frontend `.tsx` JSX and confirms coverage by grepping the
current rendered docs. Not a substitute for in-product help — this is a gap
inventory for the docs maintainers.

Legend: ✅ documented · ⚠️ partial / generic / Pro+-engine-only (OSS UI how-to thin)
· ❌ missing. "Doc drift" = a doc describes a control that no longer exists in the UI.

---

## 1. Open-source UI pages

### Home / Dashboard (`Pages/Home.tsx`)

| Element | Docs status |
|---|---|
| Dashboard page (overview, auto-refresh) | ⚠️ generic only — `getting-started/webui-overview.html` has a high-level "Dashboard Overview", no walkthrough of the gauge cards |
| Hosts / Updates / Security-Updates / Reboot-Required gauge cards (click-through) | ❌ the individual gauge cards and their navigation are undocumented |
| Antivirus Coverage card | ❌ (AV *deployment* is in `administration/antivirus-management.html`, but not the dashboard card) |
| OpenTelemetry Coverage card | ❌ |
| Dashboard Settings dialog / card-visibility toggles (`DashboardSettingsDialog`) | ❌ customizing/hiding cards not documented |

### Hosts (`Pages/Hosts.tsx`)

| Element | Docs status |
|---|---|
| Hosts list / DataGrid (status/updates/reboot/OS-upgrade chips) | ✅ `administration/host-management.html`, `getting-started/webui-overview.html` |
| Search box (fqdn/platform/ipv4/ipv6) | ⚠️ generic; search-column selector not walked through |
| Filter by Tags | ⚠️ tagging documented; the list-page tag *filter* control not walked through |
| Child-host filter toggle (All/Parents/Children, Pro+) | ❌ |
| Column Visibility button | ❌ |
| Approve Selected | ✅ `getting-started/agent-approval.html`, `administration/host-management.html` |
| Refresh All Data / Broadcast Refresh | ❌ / ⚠️ (`administration/phase8-features.html` mentions broadcast; the button isn't documented) |
| Get Diagnostics (list button) | ❌ |
| Deploy OpenTelemetry / Antivirus (bulk) | ⚠️ OTEL bulk not specific / ✅ AV `administration/antivirus-management.html` |
| Reboot / Shutdown / Update-Agent / Delete Selected (bulk) | ✅ `getting-started/host-details-walkthrough.html`, `administration/host-management.html` |
| Health grade column (Pro+) | ⚠️ `professional-plus/health-analysis.html`; list-column rendering not described |

### HostDetail (`Pages/HostDetail.tsx`)

Well covered by `getting-started/host-details-walkthrough.html` (tab-by-tab + an
Action-Menu table). Remaining gaps only:

| Element | Docs status |
|---|---|
| Tabs: Info / Hardware / Software / Software Changes / 3rd-Party Repos / Access / Security / Certificates / Server Roles / Ubuntu Pro / Diagnostics | ✅ all covered in the walkthrough |
| Compliance / Child Hosts tabs (Pro+) | ⚠️ named in walkthrough; depth in `professional-plus/compliance.html`, `child-host-management.html` |
| Plugin-injected tabs (after-info / after-security / before-diagnostics) | ❌ extensibility seam undocumented |
| Action menu: Edit Hostname/Tags, Reboot, Shutdown, Update Agent, Deploy SSH Key, Deploy Cert, Run Script (one-shot), Delete | ✅ walkthrough Action-Menu table |
| Connect to Graylog / Deploy OTEL + Start-Stop-Restart (per-host) | ⚠️ named as Pro+; modal workflow + lifecycle controls not walked through |
| Per-host **service control** (Edit Services / Start-Stop-Restart) | ❌ undocumented |
| On-demand collect/request buttons (Collect Certs/Roles, Request Host Data, Refresh Child Hosts) | ❌ undocumented |
| Create Child Host dialog (per-hypervisor fields) | ⚠️ Pro+-scoped; `child-host-management.html` (no field-level walkthrough) |

### Updates (`Pages/Updates.tsx`)

| Element | Docs status |
|---|---|
| Available-updates list + Select-All + Execute Selected | ✅ `getting-started/basic-management.html` |
| "Security Updates Only" toggle | ✅ `getting-started/basic-management.html` |
| System-only / Application-only toggles, package-manager filter, package search, pagination | ❌ |
| Per-host filter dropdown / stats cards | ⚠️ generic mention only |
| **Doc drift**: `basic-management.html` references "Settings → Update Policy" and "Updates → Schedule" — neither control exists in this page's JSX | ⚠️ fix the doc |

### OS Upgrades (`Pages/OSUpgrades.tsx`)

| Element | Docs status |
|---|---|
| OS Upgrades page (detect/list distro+macOS+Windows+BSD upgrades) | ❌ one-line mention only in `basic-management.html`; no walkthrough |
| OS-type filter, Select-All + Execute Selected OS Upgrades, stats cards, reboot warning | ❌ |
| Rollback | ❌ no rollback control exists in the JSX (doc "rollback" hits are unrelated server/app-level) |

### Reports (`Pages/Reports.tsx`) + ReportViewer (`Pages/ReportViewer.tsx`)

| Element | Docs status |
|---|---|
| Hosts tab (Registered Hosts, Hosts with Tags) + Users tab report | ✅ `server/reports.html` |
| **Security tab** (User RBAC, Firewall Status, AV Open-Source, AV Commercial, Audit Log) | ❌ not in `server/reports.html` |
| Federation tab (`FederationReportPanel`) | ⚠️ federation conceptual in `professional-plus/federation.html`; not as a Reports tab |
| View Report / Generate PDF / preview screenshots | ✅ `server/reports.html`, `professional-plus/reporting.html` |
| Pro+ gating (HTTP 402 in CE) | ✅ `server/reports.html` |
| Report search / search-by controls | ❌ |
| **Doc drift**: `professional-plus/reporting.html` describes report *scheduling*, but no schedule control exists in the Reports JSX | ⚠️ reconcile |

### Scripts (`Pages/Scripts.tsx`)

The OSS Scripts UI = 3 tabs (Library, Execute single-host, Executions history).
`professional-plus/automation-engine.html` documents the **Pro+ engine**, whose
version-history / approval / typed-parameters / cron / multi-host features are
**not in the OSS JSX** — a doc-vs-UI mismatch to reconcile.

| Element | Docs status |
|---|---|
| Script Library tab (CRUD grid) | ❌ no OSS UI guide |
| Execute tab (single host, live stdout/stderr/exit-code) | ⚠️ engine doc covers ad-hoc runs conceptually; no UI walkthrough |
| Script Executions tab (history, details, 30s refresh) | ❌ |
| Add/Edit dialog (shell + platform dropdowns, code editor) | ❌ |
| Multi-host / version history / approval / typed params / cron | ⚠️ **Pro+ engine concepts; absent from the OSS Scripts JSX** — clarify OSS-vs-Pro+ boundary |

### Secrets (`Pages/Secrets.tsx`)

| Element | Docs status |
|---|---|
| Saved-secrets grid + Add/Edit Secret dialog (CRUD) | ❌ `professional-plus/secrets.html` covers the engine/types, not this OSS CRUD UI |
| Secret types / subtypes | ✅ `professional-plus/secrets.html`, `security/secrets-management.html` |
| Vault status / unseal / rotate | ❌/❌/⚠️ — **no such controls in this page's JSX** (vault status lives in Settings → Integrations); rotation is engine-doc only |

### Settings (`Pages/Settings.tsx`)

| Element | Docs status |
|---|---|
| Email/SMTP, OpenTelemetry, Graylog, Grafana, AV defaults, Firewall defaults, Branding, Auto-Approve Tokens, Access Groups, Registration Keys, Upgrade Profiles, Package Compliance, Repo Mirroring, Authentication (LDAP/AD/OIDC) | ✅ `administration/settings-guide.html` (+ `grafana-setup`, `antivirus-management`, `firewall-management`, `compliance`, `repository-mirroring`, `external-idp`) — strong, page-aligned coverage |
| OpenBAO / Prometheus status cards | ⚠️ OpenBAO via `security/secrets-management.html`; Prometheus card not described |
| Tags / Ubuntu Pro / Distributions / Report Templates tabs | ❌ |
| Queues / Available Packages / Server Role / Host Defaults / Air-Gap Bundles tabs | ⚠️ concept covered elsewhere; tab not described |

### Third-Party Repositories (`Pages/ThirdPartyRepositories.tsx`)

| Element | Docs status |
|---|---|
| Repo table + Add dialog (PPA/COPR/OBS/Homebrew/FreeBSD/NetBSD/Chocolatey/winget) + RBAC | ✅ `administration/third-party-repositories.html` |
| Live preview of constructed repo id | ⚠️ examples shown; live-preview box not called out |
| Default vs Host-Specific source chip / select gating | ❌ |
| Enable/Disable/Delete **Selected** (bulk) | ⚠️ single actions documented; bulk not described |

### Users (`Pages/Users.tsx`) + UserDetail (`Pages/UserDetail.tsx`)

| Element | Docs status |
|---|---|
| Add / Edit user (email-based password, profile image), Lock/Unlock, Delete, RBAC gating | ✅ `administration/user-management.html` |
| Users grid (search / column visibility) | ⚠️ broad coverage; grid UI not walked through |
| UserDetail: Reset Password button/flow | ⚠️ reset-email exists; the admin button/flow not documented |
| UserDetail: Security Roles editor (grouped checkboxes, check-all/clear, save) | ⚠️ RBAC roles in `security/rbac.html`; the per-user editor UI not walked through |
| (UserDetail "profile audit log") | n/a — no such element in the JSX |

### AuditLogViewer (`Pages/AuditLogViewer.tsx`)

| Element | Docs status |
|---|---|
| Filters (search/action/entity/category/entry-type/date) + results table + pagination | ⚠️/❌ `professional-plus/audit.html` mentions query/filter; the filter set + table not enumerated |
| Export CSV | ✅ `professional-plus/audit.html` |
| Export PDF | ⚠️ doc lists CSV+JSON; **PDF export (offered in UI) not documented** |
| Pro+ license gating (HTTP 402) / Retention | ⚠️ 402 message not documented / ✅ retention documented |

### Profile (`Pages/Profile.tsx`)

| Element | Docs status |
|---|---|
| Change Password, MFA enrollment (TOTP/recovery), API Tokens, Language selector | ✅ `getting-started/profile-and-account.html` |
| Change Email tab | ⚠️ not documented (JSX notes it's a stubbed call) |
| Personal Information / Profile Image (avatar upload) tabs | ⚠️ profile pictures noted in `user-management.html`; self-service tabs not in `profile-and-account.html` |

---

## 2. Pro+ engines vs docs

Every engine with a user-facing surface has a doc page:

| Engine | Doc page | Status |
|---|---|---|
| alerting / automation / av_management / compliance / container / firewall_orchestration / fleet / health / observability / reporting / secrets / vuln | `*.html` (one each) | ✅ |
| virtualization_engine | `virtualization-engine.html` + `child-host-management.html` | ✅ |
| child_host_handlers_engine | `child-host-management.html` (shared) | ✅ |
| external_idp_engine | `external-idp.html` | ✅ |
| repository_mirroring_engine | `repository-mirroring.html` | ✅ |
| federation_controller_engine | `federation.html` | ✅ |
| federation_site_engine | `federation.html` (collective) | ⚠️ no site-specific page |
| airgap_collector_engine / airgap_repository_engine | `air-gap-deployment.html` (collective) | ⚠️ one page for the pair |
| multitenancy_engine | `enterprise-saas.html` | ✅ |
| audit_engine | `audit.html` | ✅ |

(Pure-infra `external_idp`/`federation_*`/`fleet` data-paths still have user guides where a UI surface exists.)

---

## 3. API doc gaps

`docs/api/engines.html` is a collective reference that **fully covers all 13 core
engine APIs** (automation, alerting, audit, av, compliance, containers, fleet,
firewall, health, observability, secrets, virtualization, vulns). Core OSS groups
(hosts, packages, users, reports, auth, monitoring, third-party-repos,
configuration, websockets) each have their own `docs/api/` page. ✅

Genuine REST-reference holes (conceptual page exists under `professional-plus/`,
but **no dedicated `docs/api/` endpoint reference**):

| Endpoint group | Status |
|---|---|
| `/api/v1/airgap/*` (collector/repository/schedules) | ❌ only narrative in `professional-plus/air-gap-deployment.html` |
| `/api/v1/federation/*` (+ `/site`) | ❌ only narrative in `professional-plus/federation.html` |
| control-plane / multitenancy (tenant / grant / enrollment-token / provision) | ❌ only narrative in `professional-plus/enterprise-saas.html` |
| `/upgrade-profiles`, reboot-orchestration | ⚠️ conceptual page exists; no API reference |

---

## 4. Tier classification

The Pro+ index (`professional-plus/index.html`) has a module-card grid (every
engine has a card) and a separate Professional / Enterprise / Enterprise-SaaS
tier block. Findings:

- **`multitenancy_engine`** is the only engine **without a module card** — surfaced
  only via the "Enterprise SaaS Tier" block. ⚠️
- The module cards are **not individually tier-tagged**; per-engine Professional-vs-
  Enterprise placement is prose-only in the tier block, not encoded on each card. ⚠️

---

## 5. i18n coverage

`assets/locales/` has 14 locales (`ar de en es fr hi it ja ko nl pt ru zh_CN
zh_TW`). As of 2026-06-22 there is an **outstanding re-translation backlog**: the
tone/voice rewrite pass re-seeded ~112 `[TODO]` strings per non-en locale (egregious
phrases + the 5 fluffiest-page rewrites). Process for new doc content:

1. Add new keys to `en.json` (canonical) alongside the HTML `data-i18n` attributes.
2. `i18n_validate.py --seed` propagates keys to the other 13 locales as
   `[TODO] <English>`.
3. `make translate SERVICE=http://<gpu>:8765` fills the `[TODO]`s (the docs flow
   only re-translates `[TODO]`-prefixed values, so a changed English source must be
   re-seeded to propagate).

---

## 6. Doc-vs-UI drift (fix these — docs describe controls that don't exist)

1. `getting-started/basic-management.html` → "Settings → Update Policy" and
   "Updates → Schedule": **no such controls** in `Updates.tsx`.
2. `professional-plus/reporting.html` → report *scheduling*: **no schedule control**
   in `Reports.tsx` / `ReportViewer.tsx`.
3. `professional-plus/automation-engine.html` reads as if version history / approval
   / cron / typed-params / multi-host are available in the OSS Scripts page; the OSS
   `Scripts.tsx` is **single-host, no scheduling/approval**. Clarify the OSS-vs-Pro+
   boundary.
4. `professional-plus/secrets.html` implies vault unseal/rotate as page actions;
   those controls aren't in `Secrets.tsx` (vault status lives in Settings →
   Integrations).

---

## 7. Fix-pass closure log (2026-06-22)

All ten priority items were closed in a fix-pass on 2026-06-22. New strings were
externalized through `i18n_autotag.py` (every key seeded into all 14 locales as
verbatim English in `en.json` and `[TODO] <English>` elsewhere — translation NOT
performed; run `make translate` to fill). The §1 tables above record the original
as-found state; this log records closure.

| # | Item | Status | Where |
|---|---|---|---|
| 1 | OS Upgrades page | ✅ closed | new `administration/os-upgrades.html` (detect / OS-filter / select / execute / reboot note / no-rollback), linked from `administration/index.html` |
| 2 | Scripts page (OSS UI) + automation-engine drift | ✅ closed | new `administration/scripts-guide.html` (3 tabs, single-host, explicit OSS-vs-Pro+ boundary); `automation-engine.html` already carried the boundary |
| 3 | Dashboard cards + settings dialog | ✅ closed | sections added to `getting-started/webui-overview.html` (6 gauge cards + card-visibility dialog) |
| 4 | Reports Security + Federation tabs | ✅ closed | sections added to `server/reports.html` (5 security reports + federation panel, Pro+/RBAC gating noted) |
| 5 | Doc-drift fixes (§6) | ✅ closed | `basic-management.html` "Settings → Update Policy/Schedule" reworded to the real Pro+ Update Profiles (en.json + 13 locales re-seeded); reporting/secrets rotation/scheduling clarified by the new OSS guides as engine features |
| 6 | Hosts-list controls + HostDetail service control / collect | ✅ closed | sections added to `administration/host-management.html` (7 controls) and `getting-started/host-details-walkthrough.html` (service control + on-demand collection) |
| 7 | Secrets OSS CRUD page + AuditLogViewer | ✅ closed | new `administration/secrets-guide.html` and `administration/audit-log-viewer.html` (8 filters, CSV/PDF, 402 gating), both linked |
| 8 | Settings extra tabs | ✅ closed | section added to `administration/settings-guide.html` (Tags, Ubuntu Pro, Available Packages, Distributions, Report Templates, Queues) |
| 9 | API REST references | ✅ closed | new `api/airgap.html` (41 endpoints), `api/federation.html`, `api/control-plane.html` (stub-vs-engine split documented), linked from `api/index.html` |
| 10 | `multitenancy_engine` Pro+ index card | ✅ closed | Multi-Tenancy card added to `professional-plus/index.html` |

**Remaining (low-priority / not in this pass):** per-engine tier tags on the Pro+
index cards (tiers are still prose-only in the tier block); the diffuse residual
`comprehensive`/`enterprise-grade` wording on older host pages (a separate tone
sweep, not a coverage gap); and the pending `[TODO]` translation backlog (resolved
by `make translate`, not by this docs pass).
