# SysManage Documentation Audit

A micro-level cross-reference of every UI surface (page, tab, button, dialog,
report, menu item) against the documentation under `docs/`. Goal: identify
every gap so we can close them one at a time.

Generated 2026-05-02. Not a substitute for in-the-product help — this is a
gap inventory for the docs maintainers.

Legend: ✅ documented · ⚠️ partial / generic mention only · ❌ missing.

---

## 1. Open-source UI pages

### Home / Dashboard (`Pages/Home.tsx`)

| Element | Docs status |
|---|---|
| Host count tile | ⚠️ generic mention in `getting-started/quick-start.html` |
| Stale-host indicator | ❌ |
| Pending-approvals tile | ❌ |
| Recent-activity feed | ❌ |
| OS-distribution pie chart | ❌ |

### Hosts (`Pages/Hosts.tsx`)

| Element | Docs status |
|---|---|
| Host list / search / filter | ⚠️ `getting-started/quick-start.html` |
| Approve registration button | ⚠️ mention in `security/authentication.html` |
| Bulk actions menu (delete / tag / move) | ❌ |
| Tag editor | ❌ |
| Host group filter | ⚠️ `professional-plus/fleet-engine.html` (Pro+ side) |
| Export CSV | ❌ |

### HostDetail (`Pages/HostDetail.tsx`) — TABS

| Tab | Docs status |
|---|---|
| Info | ⚠️ generic |
| Hardware | ❌ |
| Software | ❌ |
| Software Changes | ❌ |
| Third-Party Repositories | ✅ `getting-started/third-party-repositories-guide.html` |
| Access (users, groups, sudoers) | ❌ |
| Security (firewall, AV) | ⚠️ Pro+ AV doc, no OSS-side doc |
| Compliance | ✅ Pro+ doc only |
| Certificates | ⚠️ `security/mtls.html` |
| Server Roles | ❌ |
| Child Hosts (LXD/WSL/KVM/bhyve/VMM) | ⚠️ Pro+ container doc only; **no docs for KVM/bhyve/VMM child host UI** |
| Ubuntu Pro | ❌ |
| Diagnostics | ❌ |

#### HostDetail buttons / dialogs (selection)

| Element | Docs status |
|---|---|
| Edit hostname | ❌ |
| Reboot host | ⚠️ Pro+ reboot-orchestration doc covers Pro+ flow; OSS reboot button undocumented |
| Shutdown host | ❌ |
| Update agent | ❌ |
| Deploy SSH key | ❌ |
| Deploy certificate | ⚠️ `security/mtls.html` |
| Run script | ⚠️ `professional-plus/automation-engine.html` (Pro+); OSS one-shot doc missing |
| Connect to Graylog | ❌ |
| Deploy OpenTelemetry | ❌ |
| Enable / Disable virtualization (LXD, KVM, bhyve, VMM, WSL) | ❌ |
| Create child host (Container / VM / Instance dialog) | ❌ |

### Updates (`Pages/Updates.tsx`)

| Element | Docs status |
|---|---|
| Available updates list | ⚠️ `getting-started/quick-start.html` |
| Apply selected updates | ❌ |
| Update profiles (Pro+) | ⚠️ Pro+ index mentions briefly |
| Critical security toggle | ❌ |

### OS Upgrades (`Pages/OSUpgrades.tsx`)

| Element | Docs status |
|---|---|
| Detect available upgrade | ❌ |
| Apply upgrade | ❌ |
| Rollback | ❌ |

### Reports (`Pages/Reports.tsx`)

| Element | Docs status |
|---|---|
| Report list | ⚠️ `professional-plus/reporting.html` |
| Generate PDF | ⚠️ Pro+ |
| Schedule report (Pro+) | ⚠️ Pro+ |
| Per-report parameters | ❌ |

### ReportViewer (`Pages/ReportViewer.tsx`)

| Element | Docs status |
|---|---|
| Inline preview | ❌ |
| Export buttons | ❌ |

### Scripts (`Pages/Scripts.tsx`)

| Element | Docs status |
|---|---|
| Saved-script library | ✅ `professional-plus/automation-engine.html` |
| Version history | ✅ |
| Multi-host execute | ✅ |
| Per-shell support | ✅ |
| Approval workflow | ✅ |
| Script parameters | ⚠️ Pro+ doc mentions; UI usage walkthrough missing |
| Schedule | ✅ |

### Secrets (`Pages/Secrets.tsx`)

| Element | Docs status |
|---|---|
| Vault status | ⚠️ `professional-plus/secrets.html` |
| Add secret | ⚠️ |
| Vault unseal flow | ❌ |
| Vault rotate keys | ❌ |

### Settings (`Pages/Settings.tsx`)

| Element | Docs status |
|---|---|
| OpenTelemetry settings | ❌ |
| Graylog settings | ❌ |
| Antivirus default policy | ⚠️ Pro+ AV doc |
| Firewall default roles | ⚠️ Pro+ firewall doc |
| Branding (logos, report templates) | ❌ |
| Email / SMTP | ❌ |
| Auto-approve tokens | ❌ |
| Access groups | ❌ |
| Registration keys | ❌ |
| Upgrade profiles | ❌ |
| Package compliance allow/block lists | ❌ |

### Third-Party Repositories (`Pages/ThirdPartyRepositories.tsx`)

✅ `getting-started/third-party-repositories-guide.html`

### Users / UserDetail (`Pages/Users.tsx`, `UserDetail.tsx`)

| Element | Docs status |
|---|---|
| Add / edit user | ⚠️ generic in `security/authentication.html` |
| Reset password | ❌ |
| Lock / unlock | ❌ |
| Delete user | ❌ |
| Edit security roles | ⚠️ `security/rbac.html` |
| User profile audit log | ❌ |

### AuditLogViewer (`Pages/AuditLogViewer.tsx`)

| Element | Docs status |
|---|---|
| Filter by entity / action / time | ⚠️ `professional-plus/audit.html` (Pro+) |
| Export audit log | ⚠️ Pro+ |
| Retention policy | ❌ |

### Profile (`Pages/Profile.tsx`)

| Element | Docs status |
|---|---|
| Change password | ❌ |
| MFA enrollment | ❌ |
| API tokens | ❌ |
| Language selector | ❌ |

---

## 2. Pro+ engines vs docs

| Engine | Doc page | Status |
|---|---|---|
| alerting_engine | `alerting.html` | ✅ |
| audit_engine | `audit.html` | ✅ |
| automation_engine | `automation-engine.html` | ✅ |
| av_management_engine | `av-management-engine.html` | ✅ |
| compliance_engine | `compliance.html` | ✅ |
| container_engine | `container.html` | ✅ |
| firewall_orchestration_engine | `firewall-orchestration-engine.html` | ✅ |
| fleet_engine | `fleet-engine.html` | ✅ |
| health_engine | `health-analysis.html` | ✅ |
| **observability_engine** | — | ❌ **CREATE** |
| reporting_engine | `reporting.html` | ✅ |
| secrets_engine | `secrets.html` | ✅ |
| **virtualization_engine** | — | ❌ **CREATE** |
| vuln_engine | `vulnerability-scanning.html` | ✅ |
| reboot orchestration (slice of virtualization_engine) | `reboot-orchestration.html` | ✅ |

---

## 3. API doc gaps

`docs/api/` covers: authentication, configuration, hosts, monitoring, packages,
reports, third-party-repositories, users, websockets, phase8-features.

Missing dedicated endpoint references for:

- `/api/v1/automation/*` (script runtime + scheduling)
- `/api/v1/alerting/*` (rules, channels, history)
- `/api/v1/audit/*` (filtering / export)
- `/api/v1/av/*` (deploy / status / scheduling)
- `/api/v1/compliance/*` (CIS / package compliance)
- `/api/v1/containers/*` (create / lifecycle)
- `/api/v1/fleet/*` (groups / bulk ops / rolling deployments)
- `/api/v1/firewall/*` (deploy / roles / status)
- `/api/v1/health/*` (scores / history)
- `/api/v1/observability/*` (OTEL / Graylog / Grafana)
- `/api/v1/secrets/*` (Vault wrappers)
- `/api/v1/virtualization/*` (KVM / bhyve / VMM lifecycle)
- `/api/v1/vulns/*`

---

## 4. Tier classification (which feature lives where)

The Pro+ docs index lists Professional vs Enterprise tiers but multiple
recently-added engines aren't yet placed:

| Engine | Tier | Listed on Pro+ index? |
|---|---|---|
| automation_engine | Enterprise | ✅ |
| fleet_engine | Enterprise | ✅ |
| virtualization_engine | Enterprise | ❌ — only mentioned as bullet |
| observability_engine | Enterprise | ❌ |

---

## 5. i18n coverage

`assets/locales/` has `ar de en es fr hi it ja ko nl pt ru zh_CN zh_TW`.
After fixing the gaps above we need to:

1. Add new keys to `en.json` (canonical).
2. Propagate keys with English placeholder values to the other 13 locale files.
3. Mark the placeholders with a `__needs_translation__: true` companion entry
   so a translation pass can find them later.

---

## 6. Priority ordering for fix-pass

1. **virtualization_engine** doc — recently delivered Phase 10.1 work, no docs.
2. **observability_engine** doc — Phase 10.2 work, no docs.
3. **child-hosts UI walkthrough** — KVM/bhyve/VMM/LXD/WSL create/delete/start/stop dialogs are undocumented.
4. **Settings page** — OpenTelemetry, Graylog, AV defaults, firewall defaults, branding, SMTP, auto-approve tokens, access groups, registration keys, upgrade profiles, package compliance.
5. **OSS one-shot script run** + **OSS reboot button** — to disambiguate from Pro+ Automation / Reboot Orchestration.
6. **Profile / MFA / API tokens / language selector**.
7. **API endpoint references** for the engines listed above.
