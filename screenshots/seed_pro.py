#!/usr/bin/env python3
"""Seed Professional-tier engine demo data for documentation screenshots.

Runs INSIDE the screenshot VM (it imports the sysmanage ORM models, which are the
authoritative schema) and writes deterministic, fully-populated demo data straight
into the engine result tables — the same direct-to-DB philosophy as the OSS
seed_inventory.sql, so the numbers on every Professional page are stable and
controllable rather than dependent on a live scan.

Covers all seven Professional engines:
  vuln       -> vulnerability + host_vulnerability_scan + host_vulnerability_finding
  compliance -> compliance_profile + host_compliance_scan
  health     -> host_health_analysis
  alerting   -> notification_channel + alert_rule + alert_rule_notification_channel + alert
  audit      -> (none — /audit-analytics aggregates the already-seeded audit_log)
  container  -> host_child (LXD/WSL only — VM types are Enterprise virtualization)
  secrets    -> secrets (metadata only; the analytics page reads metadata, so the
                dummy vault_token/path never need to resolve against OpenBAO)

Idempotent: it clears the rows it manages (FK-safe order) and re-inserts, so it can
be run repeatedly. Apply via:  make screenshots-pro-seed
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from backend.persistence import db
from backend.persistence.models import (
    Alert,
    AlertRule,
    AlertRuleNotificationChannel,
    ComplianceProfile,
    DynamicSecretLease,
    Host,
    HostChild,
    HostComplianceScan,
    HostHealthAnalysis,
    HostPackageComplianceStatus,
    HostVulnerabilityFinding,
    HostVulnerabilityScan,
    NotificationChannel,
    PackageProfile,
    PackageProfileConstraint,
    Secret,
    Vulnerability,
)


def _now():
    # Models store naive-UTC; match that convention.
    return datetime.now(timezone.utc).replace(tzinfo=None)


NOW = _now()

# Demo hosts seeded by the OSS pass (seed.py). Engine data is attached to these.
DEMO_FQDNS = [
    "web-01.demo.sysmanage.org",
    "db-01.demo.sysmanage.org",
    "app-02.demo.sysmanage.org",
    "build-bsd.demo.sysmanage.org",
    "win-01.demo.sysmanage.org",
    "mac-01.demo.sysmanage.org",
]

# ---- shared CVE catalogue (real-ish ids) ----------------------------------
CVES = [
    # cve_id, severity, cvss, description, pkg, fixed_version
    ("CVE-2024-3094", "CRITICAL", "10.0", "Backdoor in xz/liblzma compression library.", "xz-utils", "5.6.2"),
    ("CVE-2024-6387", "HIGH", "8.1", "OpenSSH regreSSHion remote code execution.", "openssh-server", "9.8p1"),
    ("CVE-2023-44487", "HIGH", "7.5", "HTTP/2 Rapid Reset denial of service.", "nginx", "1.25.3"),
    ("CVE-2024-0727", "MEDIUM", "5.5", "OpenSSL PKCS12 NULL pointer dereference.", "openssl", "3.0.13"),
    ("CVE-2023-4911", "HIGH", "7.8", "glibc ld.so GLIBC_TUNABLES local privilege escalation.", "libc6", "2.37-6"),
    ("CVE-2024-1086", "CRITICAL", "7.8", "Linux netfilter nf_tables use-after-free LPE.", "linux-image", "6.7.2"),
    ("CVE-2023-38545", "MEDIUM", "6.5", "curl SOCKS5 heap buffer overflow.", "curl", "8.4.0"),
    ("CVE-2024-2961", "LOW", "3.7", "glibc iconv ISO-2022-CN-EXT out-of-bounds write.", "libc6", "2.39-1"),
]

# ---- per-host engine profiles ---------------------------------------------
# vuln: (total_packages, vulnerable_packages, crit, high, med, low, risk_score, risk_level)
VULN = {
    "web-01.demo.sysmanage.org": (320, 14, 2, 5, 8, 4, 82, "CRITICAL"),
    "db-01.demo.sysmanage.org": (280, 11, 1, 3, 6, 5, 68, "HIGH"),
    "app-02.demo.sysmanage.org": (260, 9, 0, 2, 5, 7, 45, "MEDIUM"),
    "build-bsd.demo.sysmanage.org": (190, 6, 1, 1, 3, 4, 55, "HIGH"),
    "win-01.demo.sysmanage.org": (410, 8, 3, 4, 2, 1, 88, "CRITICAL"),
    "mac-01.demo.sysmanage.org": (150, 4, 0, 1, 2, 3, 30, "LOW"),
}
# compliance: (total, passed, failed, error, n/a, score, grade, crit, high, med, low)
COMPLIANCE = {
    "web-01.demo.sysmanage.org": (120, 102, 15, 1, 2, 85, "B", 2, 4, 6, 3),
    "db-01.demo.sysmanage.org": (120, 110, 8, 0, 2, 92, "A", 0, 2, 4, 2),
    "app-02.demo.sysmanage.org": (110, 88, 20, 1, 1, 78, "C", 3, 5, 8, 4),
    "build-bsd.demo.sysmanage.org": (100, 85, 12, 1, 2, 84, "B", 1, 3, 5, 3),
    "win-01.demo.sysmanage.org": (130, 95, 30, 2, 3, 71, "C", 4, 8, 12, 6),
    "mac-01.demo.sysmanage.org": (90, 82, 6, 0, 2, 90, "A", 0, 1, 3, 2),
}
# Rule-level results for the Pro /compliance/<host> drill-down grid
# (ComplianceHostDetail reads scan.results = [{rule_id, rule_name, category,
# benchmark, severity, status, description, remediation}]). Failure-focused, the
# way an operator would scan it; the header badge counts come from the scan's
# count columns separately.
def _rule(rid, name, cat, sev, status, desc, rem):
    return {"rule_id": rid, "rule_name": name, "category": cat, "benchmark": "CIS",
            "severity": sev, "status": status, "description": desc, "remediation": rem}


COMPLIANCE_RULE_RESULTS = [
    _rule("1.1.1.1", "Ensure mounting of cramfs filesystems is disabled", "Filesystem", "low", "fail",
          "The cramfs filesystem type is available.", "Add 'install cramfs /bin/true' to /etc/modprobe.d/."),
    _rule("1.4.1", "Ensure bootloader password is set", "Boot", "high", "fail",
          "No GRUB superuser/password is configured.", "Set a GRUB password with grub-mkpasswd-pbkdf2."),
    _rule("1.5.1", "Ensure address space layout randomization (ASLR) is enabled", "Hardening", "medium", "pass",
          "kernel.randomize_va_space = 2.", "Set kernel.randomize_va_space = 2 in sysctl."),
    _rule("2.2.1", "Ensure time synchronization is in use", "Services", "medium", "pass",
          "chrony is installed and active.", "Install and enable chrony or systemd-timesyncd."),
    _rule("3.3.1", "Ensure source routed packets are not accepted", "Network", "high", "fail",
          "net.ipv4.conf.all.accept_source_route = 1.", "Set the sysctl to 0 and reload."),
    _rule("4.1.1.1", "Ensure auditd is installed", "Auditing", "high", "fail",
          "The auditd package is not installed.", "Install auditd and enable the service."),
    _rule("5.1.1", "Ensure cron daemon is enabled", "Services", "low", "pass",
          "cron.service is enabled.", "Enable cron via systemctl."),
    _rule("5.2.5", "Ensure SSH root login is disabled", "SSH", "critical", "fail",
          "PermitRootLogin is set to 'yes'.", "Set 'PermitRootLogin no' in sshd_config."),
    _rule("5.2.8", "Ensure SSH idle timeout interval is configured", "SSH", "medium", "fail",
          "ClientAliveInterval is unset.", "Set ClientAliveInterval 300 and ClientAliveCountMax 0."),
    _rule("5.3.1", "Ensure password creation requirements are configured", "Auth", "medium", "fail",
          "pam_pwquality minlen < 14.", "Set minlen=14 in pwquality.conf."),
    _rule("5.4.1.1", "Ensure password expiration is 365 days or less", "Auth", "low", "fail",
          "PASS_MAX_DAYS is 99999.", "Set PASS_MAX_DAYS 365 in /etc/login.defs."),
    _rule("6.1.2", "Ensure permissions on /etc/passwd are configured", "Filesystem", "medium", "pass",
          "/etc/passwd is 0644 root:root.", "chmod 644 /etc/passwd."),
    _rule("6.1.3", "Ensure permissions on /etc/shadow are configured", "Filesystem", "critical", "fail",
          "/etc/shadow is world-readable.", "chmod 0640 /etc/shadow; chown root:shadow."),
    _rule("1.3.1", "Ensure AIDE is installed", "Integrity", "high", "fail",
          "AIDE is not installed.", "Install aide and initialise the database."),
    _rule("2.1.1", "Ensure xinetd is not installed", "Services", "medium", "fail",
          "xinetd is present.", "Remove the xinetd package."),
    _rule("3.5.1.1", "Ensure a firewall package is installed", "Network", "low", "fail",
          "No firewall front-end detected.", "Install ufw or nftables."),
    _rule("4.2.1.1", "Ensure rsyslog is installed", "Logging", "medium", "error",
          "Scan could not read the rsyslog status.", "Re-run the scan with elevated privileges."),
    _rule("1.6.1.1", "Ensure SELinux/AppArmor is installed", "MAC", "low", "not_applicable",
          "Not applicable to this distribution.", "n/a"),
]

# Package-compliance profiles drive the OSS host-detail "Compliance" tab
# (HostCompliancePanel -> package_profiles + host_package_compliance_status).
# This is a DIFFERENT system from the Pro /compliance page (host_compliance_scan).
# (name, description, [(constraint_type, package, version_op, version)])
PKG_PROFILES = [
    ("Production Baseline", "Required baseline packages for production hosts.", [
        ("REQUIRED", "nginx", ">=", "1.25.3"),
        ("REQUIRED", "openssl", ">=", "3.0.13"),
        ("BLOCKED", "telnet", None, None),
    ]),
    ("Security Hardening", "Host hardening package requirements.", [
        ("REQUIRED", "fail2ban", None, None),
        ("REQUIRED", "ufw", None, None),
    ]),
]
# per host: {profile_name: (status, [(package, reason), ...])}
PKG_STATUS = {
    "web-01.demo.sysmanage.org": {
        "Production Baseline": ("NON_COMPLIANT", [
            ("nginx", "installed 1.24.0 < required 1.25.3"),
            ("telnet", "blocked package is installed"),
        ]),
        "Security Hardening": ("COMPLIANT", []),
    },
    "db-01.demo.sysmanage.org": {
        "Production Baseline": ("COMPLIANT", []),
        "Security Hardening": ("COMPLIANT", []),
    },
    "app-02.demo.sysmanage.org": {
        "Production Baseline": ("NON_COMPLIANT", [("openssl", "installed 3.0.11 < required 3.0.13")]),
        "Security Hardening": ("NON_COMPLIANT", [("fail2ban", "required package is not installed")]),
    },
    "build-bsd.demo.sysmanage.org": {
        "Production Baseline": ("COMPLIANT", []),
    },
    "win-01.demo.sysmanage.org": {
        "Security Hardening": ("NON_COMPLIANT", [
            ("ufw", "required package is not installed"),
            ("fail2ban", "required package is not installed"),
        ]),
    },
    "mac-01.demo.sysmanage.org": {
        "Production Baseline": ("COMPLIANT", []),
        "Security Hardening": ("COMPLIANT", []),
    },
}

# health: (score, grade, issues[], recommendations[])
HEALTH = {
    "web-01.demo.sysmanage.org": (82, "B",
        ["CPU utilisation sustained at 87%", "12 packages out of date", "Reboot required after kernel update"],
        ["Investigate the nginx worker load", "Apply pending package updates", "Schedule a maintenance reboot"]),
    "db-01.demo.sysmanage.org": (91, "A",
        ["3 packages out of date", "Last backup completed 26h ago"],
        ["Apply pending updates during the next window", "Verify the nightly backup schedule"]),
    "app-02.demo.sysmanage.org": (74, "C",
        ["Disk / at 78% capacity", "23 packages out of date", "Swap usage elevated"],
        ["Reclaim space under /var/log", "Apply pending updates", "Add memory or tune the app heap"]),
    "build-bsd.demo.sysmanage.org": (88, "B",
        ["7 ports out of date", "High I/O wait during builds"],
        ["Run pkg upgrade", "Move build artefacts to faster storage"]),
    "win-01.demo.sysmanage.org": (69, "C",
        ["Pending Windows updates (8)", "Defender signatures 4 days old", "Reboot required"],
        ["Install pending updates", "Force a Defender signature refresh", "Schedule a reboot"]),
    "mac-01.demo.sysmanage.org": (93, "A",
        ["2 App Store updates available"],
        ["Apply the pending App Store updates"]),
}

# Map each host's findings to a slice of the CVE catalogue (for the drill-down page).
FINDINGS = {
    "web-01.demo.sysmanage.org": [0, 1, 2, 3, 5, 6],
    "db-01.demo.sysmanage.org": [1, 3, 4, 6],
    "app-02.demo.sysmanage.org": [2, 3, 6, 7],
    "build-bsd.demo.sysmanage.org": [1, 3, 6],
    "win-01.demo.sysmanage.org": [0, 1, 4, 5],
    "mac-01.demo.sysmanage.org": [3, 7],
}

INSTALLED = {  # plausible installed (vulnerable) version per CVE index
    0: "5.6.0", 1: "8.9p1", 2: "1.24.0", 3: "3.0.11",
    4: "2.35-0", 5: "6.5.0", 6: "8.2.1", 7: "2.38-1",
}

# Container children — ONLY container types (lxd/wsl); VM types are Enterprise.
# (parent_fqdn, child_name, child_type, distribution, status)
CONTAINERS = [
    ("web-01.demo.sysmanage.org", "web-app-01", "lxd", "ubuntu-22.04", "running"),
    ("web-01.demo.sysmanage.org", "web-app-02", "lxd", "ubuntu-22.04", "running"),
    ("db-01.demo.sysmanage.org", "db-backup", "lxd", "debian-12", "running"),
    ("app-02.demo.sysmanage.org", "app-cache", "lxd", "alpine-3.20", "stopped"),
    ("win-01.demo.sysmanage.org", "wsl-ubuntu", "wsl", "Ubuntu-24.04", "running"),
    ("win-01.demo.sysmanage.org", "wsl-debian", "wsl", "Debian", "running"),
]

# Secrets metadata (vault_token/path are demo placeholders — the analytics page
# reads metadata only, so they never resolve against OpenBAO).
# Dynamic-secret leases for the Settings → Dynamic Secrets panel (reads
# dynamic_secret_lease where status=ACTIVE; OpenBAO not needed to DISPLAY them).
# (name, kind, backend_role, ttl_seconds, expires_in_min, note)
DYN_LEASES = [
    ("prod-postgres-ro", "database", "postgres-readonly", 3600, 47, "Read-only Postgres for reporting"),
    ("analytics-db-rw", "database", "analytics-rw", 7200, 104, "Analytics ETL writer"),
    ("admin-ssh-otp", "ssh", "admin", 300, 4, "Break-glass one-time SSH credential"),
    ("ci-deploy-ssh", "ssh", "deploy", 1800, 22, "CI deploy SSH key"),
    ("ci-api-token", "token", "ci-runner", 1800, 18, "Scoped API token for CI runner"),
]

SECRETS = [
    ("prod-db-password", None, "database_credentials", "postgresql"),
    ("web-01-ssh-key", "id_rsa", "ssh_key", "private"),
    ("api-github-token", None, "api_keys", "github"),
    ("wildcard-tls-cert", "star.demo.crt", "ssl_certificate", "certificate"),
    ("backup-mysql-creds", None, "database_credentials", "mysql"),
    ("monitoring-api-key", None, "api_keys", "salesforce"),
    ("ca-root-cert", "ca.crt", "ssl_certificate", "root"),
    ("deploy-ssh-key", "deploy_rsa", "ssh_key", "private"),
]

# Alert rules: (name, condition_type, params, severity)
ALERT_RULES = [
    ("Host Down — Production", "host_down", {"minutes_threshold": 10}, "critical"),
    ("Reboot Required", "reboot_required", {}, "high"),
    ("Disk Usage High", "disk_usage", {"threshold_percent": 85}, "high"),
    ("Critical CVE Detected", "cve_severity", {"min_severity": "critical"}, "critical"),
    ("Updates Available", "updates_available", {"count_threshold": 20}, "medium"),
]
# Fired alerts: (host_fqdn, rule_name, severity, title, message, age_minutes, state)
#   state: "active" | "acked" | "resolved"
ALERTS = [
    ("win-01.demo.sysmanage.org", "Critical CVE Detected", "critical",
     "Critical CVE on win-01", "CVE-2024-3094 (CVSS 10.0) detected in xz-utils.", 35, "active"),
    ("web-01.demo.sysmanage.org", "Disk Usage High", "high",
     "Disk usage high on web-01", "Filesystem / is at 91% capacity.", 120, "active"),
    ("db-01.demo.sysmanage.org", "Reboot Required", "high",
     "Reboot required on db-01", "A kernel update needs a reboot to take effect.", 240, "acked"),
    ("app-02.demo.sysmanage.org", "Updates Available", "medium",
     "Updates available on app-02", "23 package updates are pending.", 480, "active"),
    ("web-01.demo.sysmanage.org", "Critical CVE Detected", "critical",
     "Critical CVE on web-01", "CVE-2024-1086 (CVSS 7.8) detected in linux-image.", 15, "active"),
    ("build-bsd.demo.sysmanage.org", "Host Down — Production", "critical",
     "Host down: build-bsd", "No agent check-in for 12 minutes.", 720, "resolved"),
]


def main():
    session = sessionmaker(bind=db.get_engine())()
    try:
        hosts = {
            h.fqdn: h
            for h in session.query(Host).filter(Host.fqdn.in_(DEMO_FQDNS)).all()
        }
        missing = [f for f in DEMO_FQDNS if f not in hosts]
        if missing:
            print(f"  WARNING: demo hosts not found (run OSS seed first?): {missing}")
        if not hosts:
            print("  no demo hosts present — nothing to seed")
            return

        # --- idempotent reset (FK-safe order) ---
        for model in (
            Alert, AlertRuleNotificationChannel, AlertRule, NotificationChannel,
            HostVulnerabilityFinding, HostVulnerabilityScan, Vulnerability,
            HostComplianceScan, ComplianceProfile, HostHealthAnalysis,
            HostPackageComplianceStatus, PackageProfileConstraint, PackageProfile,
            HostChild, Secret, DynamicSecretLease,
        ):
            session.query(model).delete()
        session.commit()

        # --- vulnerabilities ---
        vuln_rows = {}
        for i, (cve, sev, cvss, desc, pkg, fixed) in enumerate(CVES):
            v = Vulnerability(
                cve_id=cve, severity=sev, cvss_score=cvss, cvss_version="3.1",
                description=desc, published_date=NOW - timedelta(days=30 + i),
                created_at=NOW, updated_at=NOW,
            )
            session.add(v)
            vuln_rows[i] = (v, pkg, fixed)
        session.flush()  # assign vulnerability ids for findings

        for fqdn, h in hosts.items():
            tp, vp, c, hi, m, lo, rs, rl = VULN[fqdn]
            scan = HostVulnerabilityScan(
                host_id=h.id, scanned_at=NOW - timedelta(hours=3),
                total_packages=tp, vulnerable_packages=vp,
                total_vulnerabilities=c + hi + m + lo,
                critical_count=c, high_count=hi, medium_count=m, low_count=lo,
                risk_score=rs, risk_level=rl, scanner_version="2.0.7",
                summary=f"{c} critical, {hi} high, {m} medium, {lo} low across {vp} packages.",
            )
            session.add(scan)
            session.flush()
            for idx in FINDINGS[fqdn]:
                v, pkg, fixed = vuln_rows[idx]
                session.add(HostVulnerabilityFinding(
                    scan_id=scan.id, vulnerability_id=v.id, package_name=pkg,
                    installed_version=INSTALLED[idx], fixed_version=fixed,
                    severity=v.severity, cvss_score=v.cvss_score,
                    remediation=f"Upgrade {pkg} to {fixed} or later.",
                ))

        # --- compliance ---
        profile = ComplianceProfile(
            name="CIS Distribution Independent Linux Benchmark",
            description="Center for Internet Security baseline hardening checks.",
            benchmark_type="CIS", enabled=True, created_at=NOW, updated_at=NOW,
        )
        session.add(profile)
        session.flush()
        for fqdn, h in hosts.items():
            tr, pa, fa, er, na, sc, gr, c, hi, m, lo = COMPLIANCE[fqdn]
            session.add(HostComplianceScan(
                host_id=h.id, profile_id=profile.id, scanned_at=NOW - timedelta(hours=5),
                total_rules=tr, passed_rules=pa, failed_rules=fa, error_rules=er,
                not_applicable_rules=na, compliance_score=sc, compliance_grade=gr,
                critical_failures=c, high_failures=hi, medium_failures=m, low_failures=lo,
                scanner_version="1.0.3", results=COMPLIANCE_RULE_RESULTS,
                summary=f"{pa}/{tr} rules passed — grade {gr} ({sc}%).",
            ))

        # --- package-compliance (OSS host-detail Compliance tab) ---
        pkg_profiles = {}
        for name, desc, constraints in PKG_PROFILES:
            p = PackageProfile(name=name, description=desc, enabled=True,
                               created_at=NOW, updated_at=NOW)
            session.add(p)
            session.flush()
            cmap = {}
            for ctype, pkg, op, ver in constraints:
                c = PackageProfileConstraint(
                    profile_id=p.id, package_name=pkg, constraint_type=ctype,
                    version_op=op, version=ver, created_at=NOW,
                )
                session.add(c)
                session.flush()
                cmap[pkg] = c.id
            pkg_profiles[name] = (p, cmap)
        for fqdn, h in hosts.items():
            for pname, (status, viols) in PKG_STATUS.get(fqdn, {}).items():
                p, cmap = pkg_profiles[pname]
                violations = [
                    {"constraint_id": str(cmap.get(pkg)), "package_name": pkg, "reason": reason}
                    for pkg, reason in viols
                ]
                session.add(HostPackageComplianceStatus(
                    host_id=h.id, profile_id=p.id, status=status,
                    violations=violations or None, last_scan_at=NOW - timedelta(hours=4),
                    created_at=NOW, updated_at=NOW,
                ))

        # --- health ---
        for fqdn, h in hosts.items():
            score, grade, issues, recs = HEALTH[fqdn]
            session.add(HostHealthAnalysis(
                host_id=h.id, analyzed_at=NOW - timedelta(hours=1), score=score,
                grade=grade, issues=issues, recommendations=recs,
                analysis_version="2.0.10",
            ))

        # --- alerting ---
        channel = NotificationChannel(
            name="Ops Email", channel_type="email",
            config={"recipients": ["ops@demo.sysmanage.org"]}, enabled=True,
            created_at=NOW, updated_at=NOW,
        )
        session.add(channel)
        session.flush()
        rules = {}
        for name, ctype, params, sev in ALERT_RULES:
            r = AlertRule(
                name=name, condition_type=ctype, condition_params=params,
                severity=sev, enabled=True, cooldown_minutes=60,
                created_at=NOW, updated_at=NOW,
            )
            session.add(r)
            session.flush()
            session.add(AlertRuleNotificationChannel(rule_id=r.id, channel_id=channel.id))
            rules[name] = r
        for fqdn, rule_name, sev, title, msg, age, state in ALERTS:
            if fqdn not in hosts:
                continue
            trig = NOW - timedelta(minutes=age)
            session.add(Alert(
                rule_id=rules[rule_name].id, host_id=hosts[fqdn].id, severity=sev,
                title=title, message=msg, triggered_at=trig,
                acknowledged_at=(trig + timedelta(minutes=5)) if state == "acked" else None,
                acknowledged_by="admin@sysmanage.org" if state == "acked" else None,
                resolved_at=(trig + timedelta(minutes=20)) if state == "resolved" else None,
                notification_sent=True,
            ))

        # --- containers (child hosts) ---
        for parent_fqdn, name, ctype, distro, status in CONTAINERS:
            if parent_fqdn not in hosts:
                continue
            session.add(HostChild(
                parent_host_id=hosts[parent_fqdn].id, child_host_id=None,
                child_name=name, child_type=ctype, distribution=distro,
                status=status, created_at=NOW, updated_at=NOW,
            ))

        # --- secrets (metadata only) ---
        for i, (name, filename, stype, subtype) in enumerate(SECRETS):
            session.add(Secret(
                name=name, filename=filename, secret_type=stype, secret_subtype=subtype,
                vault_token=f"hvs.DEMO{i:04d}", vault_path=f"secret/data/demo/{name}",
                created_by="admin@sysmanage.org", updated_by="admin@sysmanage.org",
            ))

        # --- dynamic-secret leases (Settings → Dynamic Secrets) ---
        for i, (name, kind, role, ttl, exp_min, note) in enumerate(DYN_LEASES):
            session.add(DynamicSecretLease(
                name=name, kind=kind, backend_role=role, ttl_seconds=ttl,
                vault_lease_id=f"{kind}/creds/{role}/demo{i:03d}",
                issued_at=NOW - timedelta(minutes=ttl // 60 - exp_min),
                expires_at=NOW + timedelta(minutes=exp_min),
                status="ACTIVE", note=note,
                secret_metadata={"backend": kind, "role": role},
            ))

        session.commit()

        print(f"  hosts seeded: {len(hosts)}")
        print(f"  vulnerabilities: {len(CVES)} CVEs, {len(hosts)} host scans, "
              f"{sum(len(v) for v in FINDINGS.values())} findings")
        print(f"  compliance: 1 profile, {len(hosts)} host scans")
        print(f"  package-compliance: {len(PKG_PROFILES)} profiles, "
              f"{sum(len(v) for v in PKG_STATUS.values())} host statuses")
        print(f"  health: {len(hosts)} analyses")
        print(f"  alerting: 1 channel, {len(ALERT_RULES)} rules, {len(ALERTS)} alerts")
        print(f"  containers: {len(CONTAINERS)} child hosts")
        print(f"  secrets: {len(SECRETS)} entries")
        print(f"  dynamic-secret leases: {len(DYN_LEASES)} active")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
