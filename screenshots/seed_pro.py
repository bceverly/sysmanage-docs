#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

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
                + gpg_key/gpg_key_assignment (the /gpg-keys list + assignments
                view; armored material stays in OpenBAO, openbao_secret_id is a
                placeholder path)
  metrics    -> custom_metric/custom_metric_tag/custom_metric_sample (the
                /custom-metrics list, define dialog + time-series graph)

Idempotent: it clears the rows it manages (FK-safe order) and re-inserts, so it can
be run repeatedly. Apply via:  make screenshots-pro-seed
"""
import os
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from backend.persistence import db
from backend.persistence.models import (
    Alert,
    AlertRule,
    AlertRuleNotificationChannel,
    ComplianceProfile,
    CustomMetric,
    CustomMetricSample,
    CustomMetricTag,
    DynamicSecretLease,
    GpgKey,
    GpgKeyAssignment,
    Host,
    HostApplicableAdvisory,
    HostChild,
    HostComplianceScan,
    HostHealthAnalysis,
    HostPackageComplianceStatus,
    HostVulnerabilityFinding,
    HostVulnerabilityScan,
    NotificationChannel,
    PackageProfile,
    PackageProfileConstraint,
    ReleaseUpgradeJob,
    Secret,
    SecurityRole,
    SharedAdvisory,
    SharedAdvisoryCve,
    SharedAdvisoryPackage,
    SharedOsLifecycle,
    Tag,
    User,
    UserSecurityRole,
    Vulnerability,
)


def _now():
    # Models store naive-UTC; match that convention.
    return datetime.now(timezone.utc).replace(tzinfo=None)


NOW = _now()

# Demo hosts seeded by the OSS pass (seed.py). Engine data is attached to these.
DEMO_FQDNS = [
    "ubuntu-web-01.corp.northstar.io",
    "rhel-db-01.corp.northstar.io",
    "debian-app-01.corp.northstar.io",
    "freebsd-build-01.corp.northstar.io",
    "win11-ws-01.corp.northstar.io",
    "macos-studio-01.corp.northstar.io",
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

# ---- shared advisory catalogue (Phase 14.1) -------------------------------
# advisory_id, source, type, severity, title, [cve_ids], [(pkg, fixed_version, release)]
ADVISORIES = [
    ("USN-6700-1", "ubuntu", "security", "HIGH", "OpenSSL vulnerabilities",
     ["CVE-2024-0727"], [("openssl", "3.0.13", "ubuntu:24.04")]),
    ("USN-6620-1", "ubuntu", "security", "CRITICAL", "Linux kernel vulnerabilities",
     ["CVE-2024-1086"], [("linux-image", "6.7.2", "ubuntu:24.04")]),
    ("RHSA-2024:1234", "redhat", "security", "HIGH", "openssh security update",
     ["CVE-2024-6387"], [("openssh-server", "9.8p1", "redhat:9")]),
    ("RHSA-2024:0987", "redhat", "bugfix", "MEDIUM", "curl bug fix update",
     ["CVE-2023-38545"], [("curl", "8.4.0", "redhat:9")]),
    ("DSA-5600-1", "debian", "security", "HIGH", "nginx security update",
     ["CVE-2023-44487"], [("nginx", "1.25.3", "debian:12")]),
    ("FreeBSD-SA-24:01.openssl", "freebsd", "security", "MEDIUM", "OpenSSL update",
     ["CVE-2024-0727"], [("openssl", "3.0.13", "freebsd:14")]),
]

# Per-host applicable advisories: fqdn -> [(advisory_id, package, installed_version)]
APPLICABLE_ADVISORIES = {
    "ubuntu-web-01.corp.northstar.io": [
        ("USN-6700-1", "openssl", "3.0.10"),
        ("USN-6620-1", "linux-image", "6.7.0"),
    ],
    "rhel-db-01.corp.northstar.io": [
        ("RHSA-2024:1234", "openssh-server", "8.7p1"),
        ("RHSA-2024:0987", "curl", "8.2.0"),
    ],
    "debian-app-01.corp.northstar.io": [
        ("DSA-5600-1", "nginx", "1.24.0"),
    ],
    "freebsd-build-01.corp.northstar.io": [
        ("FreeBSD-SA-24:01.openssl", "openssl", "3.0.10"),
    ],
}

# ---- shared OS-lifecycle registry (Phase 14.3) ----------------------------
# os_name, os_version (as the engine derives from the demo hosts' platform_release),
# codename, eol_offset_days (from now: <0 = EOL, 0..180 = approaching, else supported),
# upgrade_to, lts.  Keyed to match _host_os() output for the seeded demo fleet.
OS_LIFECYCLE = [
    ("ubuntu", "26.04", "Resolute Raccoon", 100, "26.10", True),   # approaching
    ("redhat", "10.0", None, 1800, "11", False),                   # supported
    ("debian", "13", "trixie", 900, "14", True),                   # supported
    ("freebsd", "14.3", None, -60, "14.4", False),                 # end of life
    ("windows", "11", None, 1200, None, False),                    # supported
    ("macos", "26.5", "Tahoe", 800, "27", False),                  # supported
]

# A pending release-upgrade job on the flagship host, so the host-detail OS
# Lifecycle tab shows the jobs table populated.
RELEASE_UPGRADE_JOBS = {
    "ubuntu-web-01.corp.northstar.io": ("26.04", "26.10", "do-release-upgrade", "pending"),
}

# ---- per-host engine profiles ---------------------------------------------
# vuln: (total_packages, vulnerable_packages, crit, high, med, low, risk_score, risk_level)
VULN = {
    "ubuntu-web-01.corp.northstar.io": (320, 14, 2, 5, 8, 4, 82, "CRITICAL"),
    "rhel-db-01.corp.northstar.io": (280, 11, 1, 3, 6, 5, 68, "HIGH"),
    "debian-app-01.corp.northstar.io": (260, 9, 0, 2, 5, 7, 45, "MEDIUM"),
    "freebsd-build-01.corp.northstar.io": (190, 6, 1, 1, 3, 4, 55, "HIGH"),
    "win11-ws-01.corp.northstar.io": (410, 8, 3, 4, 2, 1, 88, "CRITICAL"),
    "macos-studio-01.corp.northstar.io": (150, 4, 0, 1, 2, 3, 30, "LOW"),
}
# compliance: (total, passed, failed, error, n/a, score, grade, crit, high, med, low)
COMPLIANCE = {
    "ubuntu-web-01.corp.northstar.io": (120, 102, 15, 1, 2, 85, "B", 2, 4, 6, 3),
    "rhel-db-01.corp.northstar.io": (120, 110, 8, 0, 2, 92, "A", 0, 2, 4, 2),
    "debian-app-01.corp.northstar.io": (110, 88, 20, 1, 1, 78, "C", 3, 5, 8, 4),
    "freebsd-build-01.corp.northstar.io": (100, 85, 12, 1, 2, 84, "B", 1, 3, 5, 3),
    "win11-ws-01.corp.northstar.io": (130, 95, 30, 2, 3, 71, "C", 4, 8, 12, 6),
    "macos-studio-01.corp.northstar.io": (90, 82, 6, 0, 2, 90, "A", 0, 1, 3, 2),
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
    "ubuntu-web-01.corp.northstar.io": {
        "Production Baseline": ("NON_COMPLIANT", [
            ("nginx", "installed 1.24.0 < required 1.25.3"),
            ("telnet", "blocked package is installed"),
        ]),
        "Security Hardening": ("COMPLIANT", []),
    },
    "rhel-db-01.corp.northstar.io": {
        "Production Baseline": ("COMPLIANT", []),
        "Security Hardening": ("COMPLIANT", []),
    },
    "debian-app-01.corp.northstar.io": {
        "Production Baseline": ("NON_COMPLIANT", [("openssl", "installed 3.0.11 < required 3.0.13")]),
        "Security Hardening": ("NON_COMPLIANT", [("fail2ban", "required package is not installed")]),
    },
    "freebsd-build-01.corp.northstar.io": {
        "Production Baseline": ("COMPLIANT", []),
    },
    "win11-ws-01.corp.northstar.io": {
        "Security Hardening": ("NON_COMPLIANT", [
            ("ufw", "required package is not installed"),
            ("fail2ban", "required package is not installed"),
        ]),
    },
    "macos-studio-01.corp.northstar.io": {
        "Production Baseline": ("COMPLIANT", []),
        "Security Hardening": ("COMPLIANT", []),
    },
}

# health: (score, grade, issues[], recommendations[])
HEALTH = {
    "ubuntu-web-01.corp.northstar.io": (82, "B",
        ["CPU utilisation sustained at 87%", "12 packages out of date", "Reboot required after kernel update"],
        ["Investigate the nginx worker load", "Apply pending package updates", "Schedule a maintenance reboot"]),
    "rhel-db-01.corp.northstar.io": (91, "A",
        ["3 packages out of date", "Last backup completed 26h ago"],
        ["Apply pending updates during the next window", "Verify the nightly backup schedule"]),
    "debian-app-01.corp.northstar.io": (74, "C",
        ["Disk / at 78% capacity", "23 packages out of date", "Swap usage elevated"],
        ["Reclaim space under /var/log", "Apply pending updates", "Add memory or tune the app heap"]),
    "freebsd-build-01.corp.northstar.io": (88, "B",
        ["7 ports out of date", "High I/O wait during builds"],
        ["Run pkg upgrade", "Move build artefacts to faster storage"]),
    "win11-ws-01.corp.northstar.io": (69, "C",
        ["Pending Windows updates (8)", "Defender signatures 4 days old", "Reboot required"],
        ["Install pending updates", "Force a Defender signature refresh", "Schedule a reboot"]),
    "macos-studio-01.corp.northstar.io": (93, "A",
        ["2 App Store updates available"],
        ["Apply the pending App Store updates"]),
}

# Map each host's findings to a slice of the CVE catalogue (for the drill-down page).
FINDINGS = {
    "ubuntu-web-01.corp.northstar.io": [0, 1, 2, 3, 5, 6],
    "rhel-db-01.corp.northstar.io": [1, 3, 4, 6],
    "debian-app-01.corp.northstar.io": [2, 3, 6, 7],
    "freebsd-build-01.corp.northstar.io": [1, 3, 6],
    "win11-ws-01.corp.northstar.io": [0, 1, 4, 5],
    "macos-studio-01.corp.northstar.io": [3, 7],
}

INSTALLED = {  # plausible installed (vulnerable) version per CVE index
    0: "5.6.0", 1: "8.9p1", 2: "1.24.0", 3: "3.0.11",
    4: "2.35-0", 5: "6.5.0", 6: "8.2.1", 7: "2.38-1",
}

# Container children — ONLY container types (lxd/wsl); VM types are Enterprise.
# (parent_fqdn, child_name, child_type, distribution, status)
CONTAINERS = [
    ("ubuntu-web-01.corp.northstar.io", "web-app-01", "lxd", "ubuntu-22.04", "running"),
    ("ubuntu-web-01.corp.northstar.io", "web-app-02", "lxd", "ubuntu-22.04", "running"),
    ("rhel-db-01.corp.northstar.io", "db-backup", "lxd", "debian-12", "running"),
    ("debian-app-01.corp.northstar.io", "app-cache", "lxd", "alpine-3.20", "stopped"),
    ("win11-ws-01.corp.northstar.io", "wsl-ubuntu", "wsl", "Ubuntu-24.04", "running"),
    ("win11-ws-01.corp.northstar.io", "wsl-debian", "wsl", "Debian", "running"),
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
    ("win11-ws-01.corp.northstar.io", "Critical CVE Detected", "critical",
     "Critical CVE on win-01", "CVE-2024-3094 (CVSS 10.0) detected in xz-utils.", 35, "active"),
    ("ubuntu-web-01.corp.northstar.io", "Disk Usage High", "high",
     "Disk usage high on web-01", "Filesystem / is at 91% capacity.", 120, "active"),
    ("rhel-db-01.corp.northstar.io", "Reboot Required", "high",
     "Reboot required on db-01", "A kernel update needs a reboot to take effect.", 240, "acked"),
    ("debian-app-01.corp.northstar.io", "Updates Available", "medium",
     "Updates available on app-02", "23 package updates are pending.", 480, "active"),
    ("ubuntu-web-01.corp.northstar.io", "Critical CVE Detected", "critical",
     "Critical CVE on web-01", "CVE-2024-1086 (CVSS 7.8) detected in linux-image.", 15, "active"),
    ("freebsd-build-01.corp.northstar.io", "Host Down — Production", "critical",
     "Host down: build-bsd", "No agent check-in for 12 minutes.", 720, "resolved"),
]

# ---- GPG keys (secrets_engine — /gpg-keys) --------------------------------
# Metadata only: the LIST/assignments UI reads gpg_key/gpg_key_assignment; the
# armored material lives in OpenBAO, so openbao_secret_id is a placeholder vault
# path that never needs to resolve for these read-only screenshots.
# (name, fingerprint, key_type, has_private, comment, openbao_secret_id)
GPG_KEYS = [
    ("Release Signing Key", "3A9F 1C4E 77B2 08D5 6E1A  4F92 0C7D 88AB 1122 3344",
     "keypair", True, "Signs release artefacts and package repositories.",
     "secret/data/gpg/release-signing"),
    ("APT Repository Key", "9E22 7744 AC10 55FF 3B6D  1188 22CC 90A1 5566 7788",
     "public", False, "Public key trusted by hosts for the internal APT repo.",
     "secret/data/gpg/apt-repository"),
    ("Backup Encryption Key", "F10B 6633 21DE 4490 7C8A  55B4 3390 12EF AA99 8877",
     "keypair", True, "Encrypts off-site database backups.",
     "secret/data/gpg/backup-encryption"),
    ("Ops Team Public Key", "0044 BB99 5522 CDEF 1A2B  3C4D 6677 8899 EEFF 0011",
     "public", False, "Ops team public key for encrypted secret hand-off.",
     "secret/data/gpg/ops-team"),
]
# Assignments bind a named key to a host, or to a user on a host (target_username).
# (key_name, host_fqdn, target_username, status)
GPG_ASSIGNMENTS = [
    ("APT Repository Key", "ubuntu-web-01.corp.northstar.io", None, "installed"),
    ("APT Repository Key", "debian-app-01.corp.northstar.io", None, "pending"),
    ("Release Signing Key", "freebsd-build-01.corp.northstar.io", "builder", "installed"),
    ("Backup Encryption Key", "rhel-db-01.corp.northstar.io", "postgres", "installed"),
    ("Ops Team Public Key", "ubuntu-web-01.corp.northstar.io", "deploy", "pending"),
]

# ---- Custom metrics (observability_engine — /custom-metrics) --------------
# Each metric = a small script emitting ONE number, targeted by host tag, sampled
# on a cadence. We seed a real time-series (one sample every ~5 min for a few
# hours) per metric+host so the inline SVG graph draws an actual line.
# (name, description, interpreter, unit, cadence_seconds, script, [target_tags],
#  base_value, amplitude)  — base/amplitude shape the synthetic series.
CUSTOM_METRICS = [
    ("queue-depth", "Depth of the app job queue (pending messages).", "sh",
     "msgs", 300,
     "redis-cli LLEN jobs:pending | tr -d '\\r'",
     ["web"], 120.0, 60.0),
    ("temp-c", "CPU package temperature in degrees Celsius.", "sh",
     "°C", 300,
     "sensors -u 2>/dev/null | awk '/temp1_input/{print int($2); exit}'",
     ["production"], 52.0, 8.0),
    ("active-sessions", "Established TCP sessions on the service port.", "sh",
     "sessions", 300,
     "ss -H -t state established '( sport = :443 )' | wc -l",
     ["web"], 340.0, 90.0),
]
# How many hours of history and the sample interval (minutes) for each series.
METRIC_HISTORY_HOURS = 4
METRIC_INTERVAL_MIN = 5


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
            HostApplicableAdvisory, SharedAdvisoryCve, SharedAdvisoryPackage,
            SharedAdvisory,
            ReleaseUpgradeJob, SharedOsLifecycle,
            HostVulnerabilityFinding, HostVulnerabilityScan, Vulnerability,
            HostComplianceScan, ComplianceProfile, HostHealthAnalysis,
            HostPackageComplianceStatus, PackageProfileConstraint, PackageProfile,
            HostChild, Secret, DynamicSecretLease,
            GpgKeyAssignment, GpgKey,
            CustomMetricSample, CustomMetricTag, CustomMetric,
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

        # --- advisories (Phase 14.1) ---
        _mgr = {"ubuntu": "apt", "debian": "apt", "redhat": "dnf",
                "suse": "zypper", "freebsd": "pkg"}
        advisory_rows = {}  # identifier -> (SharedAdvisory, {pkg: fixed}, source, type, sev)
        for adv_id, source, atype, sev, title, cves, packages in ADVISORIES:
            adv = SharedAdvisory(
                advisory_id=adv_id, source=source, advisory_type=atype, severity=sev,
                title=title, affected_releases=[rel for _, _, rel in packages],
                published_date=NOW - timedelta(days=20), created_at=NOW, updated_at=NOW,
            )
            session.add(adv)
            session.flush()
            fixed_by_pkg = {}
            for pkg, fixed, rel in packages:
                session.add(SharedAdvisoryPackage(
                    advisory_row_id=adv.id, package_name=pkg,
                    package_manager=_mgr.get(source, "apt"), release=rel,
                    fixed_version=fixed, source=source, created_at=NOW, updated_at=NOW,
                ))
                fixed_by_pkg[pkg] = fixed
            for cve in cves:
                v = session.query(Vulnerability).filter(
                    Vulnerability.cve_id == cve).first()
                session.add(SharedAdvisoryCve(
                    advisory_row_id=adv.id,
                    vulnerability_id=v.id if v else None, cve_id=cve,
                ))
            advisory_rows[adv_id] = (adv, fixed_by_pkg, source, atype, sev)
        session.flush()

        for fqdn, items in APPLICABLE_ADVISORIES.items():
            h = hosts.get(fqdn)
            if not h:
                continue
            for adv_id, pkg, installed in items:
                adv, fixed_by_pkg, source, atype, sev = advisory_rows[adv_id]
                session.add(HostApplicableAdvisory(
                    host_id=h.id, advisory_id=adv.id, advisory_identifier=adv_id,
                    source=source, advisory_type=atype, severity=sev,
                    package_name=pkg, installed_version=installed,
                    fixed_version=fixed_by_pkg.get(pkg), status="applicable",
                    computed_at=NOW, created_at=NOW, updated_at=NOW,
                ))

        # --- OS lifecycle registry + release-upgrade jobs (Phase 14.3) ---
        for os_name, os_version, codename, eol_days, upgrade_to, lts in OS_LIFECYCLE:
            session.add(SharedOsLifecycle(
                os_name=os_name, os_version=os_version, codename=codename,
                release_date=NOW - timedelta(days=200),
                support_end=NOW + timedelta(days=eol_days),
                eol_date=NOW + timedelta(days=eol_days),
                lts=lts, latest_release=os_version, upgrade_to=upgrade_to,
                link="https://endoflife.date/" + os_name, source="endoflife.date",
                created_at=NOW, updated_at=NOW,
            ))
        for fqdn, (frm, to, method, status) in RELEASE_UPGRADE_JOBS.items():
            h = hosts.get(fqdn)
            if not h:
                continue
            session.add(ReleaseUpgradeJob(
                host_id=h.id, from_os_name="ubuntu", from_version=frm,
                to_version=to, method=method, status=status,
                precheck_results={"reboot_required": True, "disk_free_gb": 42,
                                  "notes": ["Full backup recommended before upgrade."]},
                created_at=NOW, updated_at=NOW,
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
            config={"recipients": ["ops@corp.northstar.io"]}, enabled=True,
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

        # --- GPG keys (secrets_engine /gpg-keys) ---
        gpg_keys = {}
        for name, fp, ktype, has_priv, comment, secret_id in GPG_KEYS:
            k = GpgKey(
                name=name, fingerprint=fp, key_type=ktype, has_private=has_priv,
                comment=comment, openbao_secret_id=secret_id,
                created_at=NOW, updated_at=NOW,
            )
            session.add(k)
            session.flush()
            gpg_keys[name] = k
        gpg_assign_count = 0
        for key_name, fqdn, target_user, status in GPG_ASSIGNMENTS:
            if fqdn not in hosts or key_name not in gpg_keys:
                continue
            session.add(GpgKeyAssignment(
                gpg_key_id=gpg_keys[key_name].id, host_id=hosts[fqdn].id,
                target_username=target_user, status=status,
                created_at=NOW, updated_at=NOW,
            ))
            gpg_assign_count += 1

        # --- grant the demo admin the two Pro+ RBAC roles these pages gate on ---
        # The secrets_engine /gpg-keys endpoints 403 unless the caller holds
        # MANAGE_GPG_KEYS, and the observability /custom-metrics endpoints gate on
        # MANAGE_CUSTOM_METRICS — is_admin is NOT honored. The initial admin only
        # gets the roles that existed WHEN it was created (create_admin_user snapshots
        # `SecurityRole.all()`), so on a VM whose admin predates the m1gpgkeys /
        # n1custmetric migrations these two roles are missing and the pages render
        # empty. Grant them idempotently here, matching create_admin_user's pattern
        # (one UserSecurityRole row per role, self-granted).
        admin_userid = os.environ.get("SCREENSHOT_ADMIN", "admin@sysmanage.org")
        admin = session.query(User).filter(User.userid == admin_userid).first()
        granted_role_count = 0
        if admin is None:
            print(f"  WARNING: demo admin {admin_userid} not found — cannot grant "
                  "MANAGE_GPG_KEYS / MANAGE_CUSTOM_METRICS")
        else:
            for role_name in ("Manage GPG Keys", "Manage Custom Metrics"):
                role = (
                    session.query(SecurityRole)
                    .filter(SecurityRole.name == role_name)
                    .first()
                )
                if role is None:
                    print(f"  WARNING: role '{role_name}' missing (run migrations?)")
                    continue
                already = (
                    session.query(UserSecurityRole)
                    .filter(
                        UserSecurityRole.user_id == admin.id,
                        UserSecurityRole.role_id == role.id,
                    )
                    .first()
                )
                if already is None:
                    session.add(UserSecurityRole(
                        user_id=admin.id, role_id=role.id,
                        granted_by=admin.id, granted_at=NOW,
                    ))
                    granted_role_count += 1

        # --- custom metrics (observability_engine /custom-metrics) ---
        # Resolve the demo tags (created by the OSS seed) and the hosts carrying
        # each tag, so metric samples land on real tag-targeted hosts.
        tags_by_name = {t.name: t for t in session.query(Tag).all()}
        metric_sample_count = 0
        n_steps = (METRIC_HISTORY_HOURS * 60) // METRIC_INTERVAL_MIN
        for (name, desc, interp, unit, cadence, script,
             target_tags, base, amp) in CUSTOM_METRICS:
            metric = CustomMetric(
                name=name, description=desc, script=script, interpreter=interp,
                unit=unit, cadence_seconds=cadence, enabled=True,
                created_at=NOW, updated_at=NOW,
            )
            session.add(metric)
            session.flush()
            # Targeting: attach the metric to each existing demo tag.
            target_hosts = {}
            for tag_name in target_tags:
                tag = tags_by_name.get(tag_name)
                if tag is None:
                    continue
                session.add(CustomMetricTag(
                    custom_metric_id=metric.id, tag_id=tag.id,
                ))
                for h in getattr(tag, "hosts", []):
                    if h.fqdn in hosts:
                        target_hosts[h.fqdn] = h
            # Fallback: if tag→host links aren't present, still graph on the
            # obviously-matching demo hosts so the shot never renders empty.
            if not target_hosts:
                for fqdn, h in hosts.items():
                    if any(tt in fqdn.split(".")[0] for tt in ("web", "db")):
                        target_hosts[fqdn] = h
            # Deterministic time-series: one sample every METRIC_INTERVAL_MIN
            # minutes over the last METRIC_HISTORY_HOURS, gently varying so the
            # SVG line chart draws a real, non-flat curve.
            for hi, (fqdn, h) in enumerate(sorted(target_hosts.items())):
                for step in range(n_steps + 1):
                    minutes_ago = (n_steps - step) * METRIC_INTERVAL_MIN
                    # triangular wave in [0,1], phase-shifted per host — no math import
                    phase = (step + hi * 7) % 24
                    wave = phase / 12.0 if phase <= 12 else (24 - phase) / 12.0
                    value = round(base + amp * (wave - 0.5) * 2 + (hi * amp * 0.15), 1)
                    session.add(CustomMetricSample(
                        custom_metric_id=metric.id, host_id=h.id,
                        value=value, status="ok",
                        collected_at=NOW - timedelta(minutes=minutes_ago),
                    ))
                    metric_sample_count += 1

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
        print(f"  gpg keys: {len(GPG_KEYS)} keys, {gpg_assign_count} assignments")
        print(f"  custom metrics: {len(CUSTOM_METRICS)} metrics, "
              f"{metric_sample_count} samples")
        print(f"  admin RBAC roles granted: {granted_role_count} "
              "(MANAGE_GPG_KEYS / MANAGE_CUSTOM_METRICS)")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
