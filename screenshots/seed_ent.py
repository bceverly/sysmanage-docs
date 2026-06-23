#!/usr/bin/env python3
"""Seed Enterprise-tier engine demo data for documentation screenshots.

Runs INSIDE the screenshot VM (imports the sysmanage ORM models, the authoritative
schema) and writes deterministic COMPLETED-STATE rows straight into the engine
result tables — same direct-to-DB philosophy as seed_pro.py, so every Enterprise
page looks populated without real topology (no live VMs / federated sites / ISOs).

Run AFTER make screenshots-seed (demo hosts) and make screenshots-pro-seed (the Pro
engine data Enterprise also shows). Apply via:  make screenshots-ent-seed

Covers the Enterprise-only engines:
  av_management        -> antivirus_default + antivirus_status + commercial_antivirus_status
  firewall_orch        -> firewall_role + firewall_role_open_port + host_firewall_role + firewall_status
  automation           -> upgrade_profiles + saved_scripts + script_execution_log
  repository_mirroring -> mirror_repository + mirror_snapshot
  access_groups        -> access_groups + registration_keys
  virtualization       -> host_child (VM types: kvm/bhyve — leaves seed_pro's lxd/wsl alone)
  observability        -> grafana_integration_settings + graylog_integration_settings
  external_idp         -> external_idp_provider + idp_role_mapping + external_idp_settings
  federation           -> federation_sites + federation_host_directory
  air-gap              -> airgap_collection_run + airgap_collection_target + airgap_media_manifest
                          + airgap_local_repository

Idempotent: clears the rows it manages (FK-safe order) then re-inserts.
NOTE: fleet_engine has NO OSS model (engine-owned tables) — its host-detail tab is
not seeded here.
"""
import json
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from backend.persistence import db
from backend.persistence.models import (
    AccessGroup,
    AntivirusDefault,
    AntivirusStatus,
    CommercialAntivirusStatus,
    ExternalIdpProvider,
    ExternalIdpSettings,
    FederationHostDirectory,
    FederationSite,
    FirewallRole,
    FirewallRoleOpenPort,
    FirewallStatus,
    GrafanaIntegrationSettings,
    GraylogIntegrationSettings,
    Host,
    HostChild,
    HostFirewallRole,
    IdpRoleMapping,
    MirrorRepository,
    MirrorSnapshot,
    RegistrationKey,
    SavedScript,
    ScriptExecutionLog,
    UpgradeProfile,
    User,
)
# Air-gap models aren't re-exported from the package __init__ — import directly.
from backend.persistence.models.airgap import (
    AirgapCollectionRun,
    AirgapCollectionTarget,
    AirgapLocalRepository,
    AirgapMediaManifest,
)


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


NOW = _now()

DEMO_FQDNS = [
    "web-01.demo.sysmanage.org",
    "db-01.demo.sysmanage.org",
    "app-02.demo.sysmanage.org",
    "build-bsd.demo.sysmanage.org",
    "win-01.demo.sysmanage.org",
    "mac-01.demo.sysmanage.org",
]

# ---- antivirus -------------------------------------------------------------
AV_DEFAULTS = [  # (os_name, antivirus_package)
    ("Ubuntu", "clamav"), ("Debian", "clamav"), ("Fedora", "clamav"),
    ("FreeBSD", "clamav"), ("macOS", "clamav"), ("Windows", "windows-defender"),
]
# per host: (software_name, version, enabled) — linux/bsd/mac use ClamAV
AV_STATUS = {
    "web-01.demo.sysmanage.org": ("ClamAV", "1.0.5", True),
    "db-01.demo.sysmanage.org": ("ClamAV", "1.0.5", True),
    "app-02.demo.sysmanage.org": ("ClamAV", "1.0.3", True),
    "build-bsd.demo.sysmanage.org": ("ClamAV", "1.0.5", True),
    "mac-01.demo.sysmanage.org": ("ClamAV", "1.0.5", False),
}

# ---- firewall --------------------------------------------------------------
FW_ROLES = [  # (name, [(port, tcp, udp)])
    ("web-server", [(80, True, False), (443, True, False)]),
    ("db-server", [(5432, True, False)]),
    ("ssh-admin", [(22, True, False)]),
    ("monitoring", [(9090, True, False), (3000, True, False)]),
]
# per host: (firewall_name, enabled, ipv4_ports[list of {port,protocols}], role)
FW_STATUS = {
    "web-01.demo.sysmanage.org": ("ufw", True, ["22", "80", "443"], "web-server"),
    "db-01.demo.sysmanage.org": ("ufw", True, ["22", "5432"], "db-server"),
    "app-02.demo.sysmanage.org": ("firewalld", True, ["22", "8080"], "ssh-admin"),
    "build-bsd.demo.sysmanage.org": ("pf", True, ["22"], "ssh-admin"),
    "win-01.demo.sysmanage.org": ("Windows Firewall", True, ["3389", "445"], None),
    "mac-01.demo.sysmanage.org": ("pf", False, ["22"], None),
}

# ---- automation ------------------------------------------------------------
SCRIPTS = [  # (name, shell, platform, content, description)
    ("Restart Nginx", "bash", "linux", "systemctl restart nginx",
     "Gracefully restart the nginx service."),
    ("Disk Usage Report", "bash", "linux", "df -h --output=pcent,target | sort -r",
     "Report filesystem usage, highest first."),
    ("Pending Reboot Check", "bash", "linux", "[ -f /var/run/reboot-required ] && echo REBOOT",
     "Flag hosts that need a reboot."),
    ("Windows Update Status", "powershell", "windows",
     "Get-WindowsUpdate | Measure-Object | Select Count",
     "Count pending Windows updates."),
]
# (host_fqdn, script_name, status, exit_code, stdout, age_min)
SCRIPT_RUNS = [
    ("web-01.demo.sysmanage.org", "Restart Nginx", "completed", 0, "nginx restarted", 30),
    ("db-01.demo.sysmanage.org", "Disk Usage Report", "completed", 0, "12% /", 90),
    ("app-02.demo.sysmanage.org", "Pending Reboot Check", "completed", 0, "REBOOT", 200),
    ("win-01.demo.sysmanage.org", "Windows Update Status", "completed", 0, "Count: 8", 45),
    ("web-01.demo.sysmanage.org", "Disk Usage Report", "running", None, "", 2),
]

# ---- upgrade profiles ------------------------------------------------------
UPGRADE_PROFILES = [  # (name, description, cron, security_only, last_status, mgrs)
    ("Weekly security — Sat 02:00", "Security-only updates every Saturday at 02:00.",
     "0 2 * * 6", True, "SUCCESS", "apt,dnf"),
    ("Monthly full — 1st 03:00", "All pending updates on the first of the month.",
     "0 3 1 * *", False, "SUCCESS", None),
    ("Nightly desktops", "Nightly updates for workstation hosts.",
     "0 1 * * *", False, "SKIPPED", "apt"),
]

# ---- repository mirroring --------------------------------------------------
MIRRORS = [  # (name, pkg_mgr, upstream, suite, components, arch, size, files)
    ("ubuntu-jammy-main", "apt", "http://archive.ubuntu.com/ubuntu", "jammy",
     "main restricted universe", "amd64", 88_000_000_000, 142000),
    ("ubuntu-jammy-security", "apt", "http://security.ubuntu.com/ubuntu", "jammy-security",
     "main restricted", "amd64", 9_400_000_000, 18400),
    ("rocky-9-baseos", "dnf", "https://dl.rockylinux.org/pub/rocky/9/BaseOS", None,
     None, "x86_64", 12_700_000_000, 9100),
    ("freebsd-14-latest", "pkg", "https://pkg.freebsd.org/FreeBSD:14:amd64/latest", None,
     None, "amd64", 31_000_000_000, 33500),
]

# ---- access groups ---------------------------------------------------------
ACCESS_GROUPS = [  # (name, parent_name_or_None, description)
    ("Datacenter East", None, "Primary east-coast datacenter."),
    ("Web Tier", "Datacenter East", "Public-facing web servers."),
    ("Database Tier", "Datacenter East", "Database servers."),
    ("Datacenter West", None, "West-coast datacenter."),
]
REG_KEYS = [  # (name, group_name, auto_approve, max_uses, expires_days)
    ("east-web-enroll", "Web Tier", True, 50, 90),
    ("west-bootstrap", "Datacenter West", False, None, 30),
]

# ---- external IdP ----------------------------------------------------------
IDP_MAPPINGS = [  # (external_group, role_name, default_for_unmapped)
    ("CN=SysAdmins,OU=Groups,DC=corp,DC=example", "Administrator", False),
    ("CN=Operators,OU=Groups,DC=corp,DC=example", "Operator", False),
    ("oidc:viewers", "Viewer", True),
]

# ---- federation sites ------------------------------------------------------
FED_SITES = [  # (name, location, url, status, conn, host_count, lat, lon, cc)
    ("us-east-1", "Ashburn, VA", "https://us-east-1.fed.sysmanage.org", "enrolled",
     "connected", 142, 39.0438, -77.4874, "US"),
    ("eu-west-1", "Dublin, IE", "https://eu-west-1.fed.sysmanage.org", "enrolled",
     "connected", 87, 53.3498, -6.2603, "IE"),
    ("ap-south-1", "Singapore", "https://ap-south-1.fed.sysmanage.org", "enrolled",
     "degraded", 53, 1.3521, 103.8198, "SG"),
    ("us-west-2", "Portland, OR", "https://us-west-2.fed.sysmanage.org", "pending",
     None, 0, 45.5152, -122.6784, "US"),
]

# ---- virtualization (VM child hosts; seed_pro owns the lxd/wsl containers) --
VMS = [  # (parent_fqdn, child_name, child_type, distribution, status)
    ("db-01.demo.sysmanage.org", "vm-pg-replica", "kvm", "ubuntu-22.04", "running"),
    ("db-01.demo.sysmanage.org", "vm-pg-analytics", "kvm", "rocky-9", "running"),
    ("web-01.demo.sysmanage.org", "vm-staging", "kvm", "ubuntu-24.04", "stopped"),
    ("build-bsd.demo.sysmanage.org", "vm-bsd-ci", "bhyve", "freebsd-14", "running"),
]

# ---- air-gap ---------------------------------------------------------------
AIRGAP_TARGETS = [  # (distro, version, repos, bytes, files)
    ("ubuntu", "22.04", "main,security,universe", 88_000_000_000, 142000),
    ("rocky", "9", "BaseOS,AppStream", 12_700_000_000, 9100),
    ("freebsd", "14", "latest", 31_000_000_000, 33500),
]
AIRGAP_REPOS = [  # (distro, version, repo_url, package_count, age_hours)
    ("ubuntu", "22.04", "http://airgap.local/ubuntu", 142000, 6),
    ("rocky", "9", "http://airgap.local/rocky", 9100, 6),
    ("freebsd", "14", "http://airgap.local/freebsd", 33500, 30),
]


def main():
    session = sessionmaker(bind=db.get_engine())()
    try:
        hosts = {
            h.fqdn: h
            for h in session.query(Host).filter(Host.fqdn.in_(DEMO_FQDNS)).all()
        }
        if not hosts:
            print("  no demo hosts present — run make screenshots-seed first")
            return
        missing = [f for f in DEMO_FQDNS if f not in hosts]
        if missing:
            print(f"  WARNING: demo hosts not found: {missing}")

        # UUID of the admin user — for GUID created_by columns that are FKs to
        # `user` (FirewallRole, HostFirewallRole, AirgapCollectionRun). String
        # created_by columns (SavedScript, ScriptExecutionLog) keep the email.
        admin = (
            session.query(User).filter_by(userid="admin@sysmanage.org").first()
            or session.query(User).first()
        )
        admin_id = admin.id if admin else None

        # --- idempotent reset (FK-safe order) ---
        for model in (
            HostFirewallRole, FirewallRoleOpenPort, FirewallRole, FirewallStatus,
            AntivirusStatus, CommercialAntivirusStatus,
            ScriptExecutionLog, SavedScript, UpgradeProfile,
            MirrorSnapshot, MirrorRepository,
            RegistrationKey, AccessGroup,
            IdpRoleMapping, ExternalIdpProvider, ExternalIdpSettings,
            FederationHostDirectory, FederationSite,
            GrafanaIntegrationSettings, GraylogIntegrationSettings,
            AirgapMediaManifest, AirgapCollectionTarget, AirgapCollectionRun,
            AirgapLocalRepository,
        ):
            session.query(model).delete()
        # Virtualization: only clear the VM-type child hosts (leave seed_pro's lxd/wsl).
        session.query(HostChild).filter(
            HostChild.child_type.in_(["kvm", "bhyve", "vmm"])
        ).delete(synchronize_session=False)
        session.commit()

        # --- antivirus ---
        # Configure a default AV package for EVERY OS that already has an
        # antivirus_default row (migration-seeded) rather than wiping the set and
        # inserting a few — otherwise most OSes render "None". ClamAV is the
        # cross-platform default; Windows (if present) keeps its own default.
        for d in session.query(AntivirusDefault).all():
            if (d.os_name or "").lower().startswith("windows"):
                continue
            d.antivirus_package = "clamav"
            d.updated_at = NOW
        for fqdn, (name, ver, enabled) in AV_STATUS.items():
            if fqdn not in hosts:
                continue
            session.add(AntivirusStatus(
                host_id=hosts[fqdn].id, software_name=name,
                install_path="/usr/bin/clamscan", version=ver,
                enabled=enabled, last_updated=NOW - timedelta(hours=6),
            ))
        if "win-01.demo.sysmanage.org" in hosts:
            session.add(CommercialAntivirusStatus(
                host_id=hosts["win-01.demo.sysmanage.org"].id,
                product_name="Microsoft Defender", product_version="4.18.24010",
                service_enabled=True, antivirus_enabled=True,
                realtime_protection_enabled=True, antispyware_enabled=True,
                tamper_protection_enabled=True, full_scan_age=2, quick_scan_age=0,
                signature_version="1.405.1234.0",
                signature_last_updated=NOW - timedelta(hours=8),
                created_at=NOW, last_updated=NOW - timedelta(hours=8),
            ))

        # --- firewall ---
        roles = {}
        for name, ports in FW_ROLES:
            r = FirewallRole(name=name, created_at=NOW, created_by=admin_id)
            session.add(r)
            session.flush()
            roles[name] = r
            for port, tcp, udp in ports:
                session.add(FirewallRoleOpenPort(
                    firewall_role_id=r.id, port_number=port, tcp=tcp, udp=udp,
                    ipv4=True, ipv6=True,
                ))
        for fqdn, (fwname, enabled, v4ports, role) in FW_STATUS.items():
            if fqdn not in hosts:
                continue
            ipv4 = [{"port": p, "protocols": ["tcp"]} for p in v4ports]
            session.add(FirewallStatus(
                host_id=hosts[fqdn].id, firewall_name=fwname, enabled=enabled,
                tcp_open_ports=json.dumps(v4ports), udp_open_ports=json.dumps([]),
                ipv4_ports=json.dumps(ipv4), ipv6_ports=json.dumps([]),
                last_updated=NOW - timedelta(hours=4),
            ))
            if role and role in roles:
                session.add(HostFirewallRole(
                    host_id=hosts[fqdn].id, firewall_role_id=roles[role].id,
                    created_at=NOW, created_by=admin_id,
                ))

        # --- automation: saved scripts + executions ---
        saved = {}
        for name, shell, platform, content, desc in SCRIPTS:
            s = SavedScript(
                name=name, description=desc, content=content, shell_type=shell,
                platform=platform, is_active=True, created_by="admin@sysmanage.org",
                created_at=NOW, updated_at=NOW,
            )
            session.add(s)
            session.flush()
            saved[name] = s
        for i, (fqdn, sname, status, code, out, age) in enumerate(SCRIPT_RUNS):
            if fqdn not in hosts:
                continue
            trig = NOW - timedelta(minutes=age)
            session.add(ScriptExecutionLog(
                execution_id=f"demo-exec-{i:04d}", host_id=hosts[fqdn].id,
                saved_script_id=saved[sname].id, script_name=sname,
                script_content=saved[sname].content, shell_type=saved[sname].shell_type,
                status=status, requested_by="admin@sysmanage.org", started_at=trig,
                completed_at=(trig + timedelta(seconds=3)) if status == "completed" else None,
                exit_code=code, stdout_output=out,
                created_at=trig, updated_at=trig,
            ))

        # --- upgrade profiles ---
        for name, desc, cron, sec_only, last_status, mgrs in UPGRADE_PROFILES:
            session.add(UpgradeProfile(
                name=name, description=desc, cron=cron, enabled=True,
                security_only=sec_only, package_managers=mgrs,
                last_run=NOW - timedelta(days=2), last_status=last_status,
                next_run=NOW + timedelta(days=1), created_at=NOW, updated_at=NOW,
            ))

        # --- repository mirroring ---
        # Mirrors are host-scoped (the host that serves the mirror). Attach them
        # to a demo host (host_id is NOT NULL).
        mirror_host_id = next(iter(hosts.values())).id
        mirror_ids = []  # reused by the air-gap collection targets below
        for name, mgr, upstream, suite, comps, arch, size, files in MIRRORS:
            r = MirrorRepository(
                name=name, package_manager=mgr, upstream_url=upstream, suite=suite,
                components=comps, architectures=arch, enabled=True, host_id=mirror_host_id,
                last_sync_at=NOW - timedelta(hours=5), last_sync_status="success",
                last_snapshot_at=NOW - timedelta(hours=5), last_snapshot_status="success",
                next_sync_at=NOW + timedelta(hours=19),
                created_at=NOW, updated_at=NOW,
            )
            session.add(r)
            session.flush()
            mirror_ids.append(r.id)
            session.add(MirrorSnapshot(
                repository_id=r.id, snapshot_id=NOW.strftime("%Y%m%dT%H%M%S"),
                taken_at=NOW - timedelta(hours=5), size_bytes=size, file_count=files,
                retention_until=NOW + timedelta(days=30),
            ))

        # --- access groups + registration keys ---
        groups = {}
        for name, parent, desc in ACCESS_GROUPS:
            g = AccessGroup(
                name=name, description=desc,
                parent_id=groups[parent].id if parent and parent in groups else None,
                created_at=NOW, updated_at=NOW,
            )
            session.add(g)
            session.flush()
            groups[name] = g
        for name, grp, auto, max_uses, exp_days in REG_KEYS:
            session.add(RegistrationKey(
                name=name, access_group_id=groups[grp].id if grp in groups else None,
                auto_approve=auto, max_uses=max_uses, use_count=3 if max_uses else 0,
                expires_at=NOW + timedelta(days=exp_days), created_at=NOW,
            ))

        # --- observability integrations ---
        session.add(GrafanaIntegrationSettings(
            id=1, enabled=True, use_managed_server=True,
            manual_url="https://grafana.demo.sysmanage.org",
            created_at=NOW, updated_at=NOW,
        ))
        session.add(GraylogIntegrationSettings(
            enabled=True, use_managed_server=True,
            manual_url="https://graylog.demo.sysmanage.org",
            has_gelf_tcp=True, gelf_tcp_port=12201,
            has_syslog_udp=True, syslog_udp_port=1514,
            inputs_last_checked=NOW - timedelta(minutes=10),
            created_at=NOW, updated_at=NOW,
        ))

        # --- external IdP ---
        ldap = ExternalIdpProvider(
            name="Corporate AD", type="ldap", enabled=True,
            ldap_server_url="ldaps://ad.corp.example:636",
            ldap_bind_dn="CN=svc-sysmanage,OU=Service,DC=corp,DC=example",
            ldap_user_search_base="OU=Users,DC=corp,DC=example",
            ldap_user_search_filter="(sAMAccountName={username})",
            ldap_group_search_base="OU=Groups,DC=corp,DC=example",
            created_at=NOW, updated_at=NOW,
        )
        oidc = ExternalIdpProvider(
            name="Okta SSO", type="oidc", enabled=True,
            oidc_issuer_url="https://corp.okta.com",
            oidc_client_id="0oa1demo2sysmanage",
            oidc_redirect_uri="https://sysmanage.demo.org/api/auth/oidc/callback",
            oidc_discovery_url="https://corp.okta.com/.well-known/openid-configuration",
            created_at=NOW, updated_at=NOW,
        )
        session.add(ldap)
        session.add(oidc)
        session.flush()
        for ext_group, role, default in IDP_MAPPINGS:
            provider = oidc if ext_group.startswith("oidc:") else ldap
            session.add(IdpRoleMapping(
                provider_id=provider.id, external_group=ext_group,
                role_name=role, default_for_unmapped=default, created_at=NOW,
            ))
        session.add(ExternalIdpSettings(local_account_fallback=True, max_failed_attempts=5))

        # --- federation sites + host directory ---
        for name, loc, url, status, conn, hc, lat, lon, cc in FED_SITES:
            s = FederationSite(
                name=name, location_label=loc, url=url, status=status,
                connection_state=conn, host_count=hc,
                last_sync_at=NOW - timedelta(minutes=3) if status == "enrolled" else None,
                last_sync_status="success" if conn == "connected" else (
                    "degraded" if conn == "degraded" else None),
                enrolled_at=NOW - timedelta(days=30) if status == "enrolled" else None,
                sysmanage_version="2.3.0.0", geo_latitude=lat, geo_longitude=lon,
                geo_country_code=cc, created_at=NOW, updated_at=NOW,
            )
            session.add(s)
            session.flush()
            # a few directory hosts so the coordinator host-count looks real
            for n in range(min(hc, 3)):
                session.add(FederationHostDirectory(
                    host_id=uuid.uuid4(), site_id=s.id,
                    fqdn=f"host-{n+1:02d}.{name}.internal", os_family="Linux",
                    os_version="Ubuntu 22.04", platform="linux", status="up",
                    last_seen=NOW - timedelta(minutes=5),
                    geo_latitude=lat, geo_longitude=lon, geo_country_code=cc,
                    mtime=NOW,
                ))

        # --- virtualization VMs (KVM/bhyve child hosts) ---
        for parent_fqdn, name, ctype, distro, status in VMS:
            if parent_fqdn not in hosts:
                continue
            session.add(HostChild(
                parent_host_id=hosts[parent_fqdn].id, child_host_id=None,
                child_name=name, child_type=ctype, distribution=distro,
                status=status, created_at=NOW, updated_at=NOW,
            ))

        # --- air-gap: one completed collection run + manifest + local repos ---
        run = AirgapCollectionRun(
            iso_label="airgap-2026-06-22", media_size_bytes=4_700_000_000,
            include_cve=True, include_compliance=True, status="COMPLETE",
            started_at=NOW - timedelta(hours=3), completed_at=NOW - timedelta(hours=1),
            created_at=NOW - timedelta(hours=3), created_by=admin_id,
        )
        session.add(run)
        session.flush()
        for i, (distro, ver, repos, byts, files) in enumerate(AIRGAP_TARGETS):
            # mirror_id must be a non-empty mirror id — the runs API serializes it
            # into RunTargetSpec (min_length=1) and 500s on an empty string.
            session.add(AirgapCollectionTarget(
                run_id=run.id, distro=distro, version=ver, repos=repos,
                byte_count=byts, file_count=files, status="COMPLETE",
                mirror_id=mirror_ids[i % len(mirror_ids)] if mirror_ids else None,
            ))
        session.add(AirgapMediaManifest(
            run_id=run.id, disc_index=1, disc_count=1,
            iso_path="/var/lib/sysmanage/airgap/airgap-2026-06-22.iso",
            iso_sha256="a" * 64, iso_size_bytes=4_690_000_000,
            manifest_json=json.dumps({"targets": len(AIRGAP_TARGETS), "files": 184600}),
            signature="demo-signature", signer_fingerprint="b" * 64,
            created_at=NOW - timedelta(hours=1),
        ))
        for distro, ver, url, pkgs, age in AIRGAP_REPOS:
            session.add(AirgapLocalRepository(
                distro=distro, version=ver, repo_url=url, package_count=pkgs,
                last_ingest_at=NOW - timedelta(hours=age),
            ))

        session.commit()

        print(f"  hosts: {len(hosts)}")
        print(f"  antivirus: {len(AV_DEFAULTS)} defaults, {len(AV_STATUS)} host statuses, 1 commercial")
        print(f"  firewall: {len(FW_ROLES)} roles, {len(FW_STATUS)} host statuses")
        print(f"  automation: {len(SCRIPTS)} scripts, {len(SCRIPT_RUNS)} executions")
        print(f"  upgrade profiles: {len(UPGRADE_PROFILES)}")
        print(f"  mirrors: {len(MIRRORS)} repos (+ snapshots)")
        print(f"  access groups: {len(ACCESS_GROUPS)} (+ {len(REG_KEYS)} keys)")
        print("  observability: grafana + graylog integrations")
        print(f"  external IdP: 2 providers, {len(IDP_MAPPINGS)} role mappings")
        print(f"  virtualization: {len(VMS)} VM child hosts (kvm/bhyve)")
        print(f"  federation: {len(FED_SITES)} sites (+ directory hosts)")
        print(f"  air-gap: 1 collection run, {len(AIRGAP_TARGETS)} targets, {len(AIRGAP_REPOS)} repos")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
