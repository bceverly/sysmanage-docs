#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Seed configuration-management + drift demo data (Phase 20.1 / 20.2).

Runs INSIDE the screenshot VM against the sysmanage ORM, same direct-to-DB
approach as seed_pro.py / seed_ent.py. Apply via:  make screenshots-cfg-seed

WHY THIS IS ITS OWN SEEDER RATHER THAN PART OF seed_ent.py
----------------------------------------------------------
seed_ent.py sits at exactly the repo's 1000-line ceiling, and the seeders are
piped to the VM over stdin (``cat seed_ent.py | vagrant ssh``), so a sibling
module cannot simply be imported into it -- there is no importable file on the
far side. One more seeder with its own target is the pattern the repo already
uses four times (seed, seed_pro, seed_ent, seed_fleet), so this follows it.

Covers:
  config_management_engine -> config_profile + config_profile_version
                              + config_profile_assignment + config_drift_finding

Run AFTER make screenshots-seed (demo hosts). Idempotent: clears the rows it
manages (FK-safe order) then re-inserts.
"""
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from backend.persistence import db
from backend.persistence.models import (
    ConfigDriftFinding,
    ConfigProfile,
    ConfigProfileAssignment,
    ConfigProfileVersion,
    Host,
)

AUTHOR = "admin@sysmanage.org"

DEMO_FQDNS = [
    "ubuntu-web-01.corp.northstar.io",
    "rhel-db-01.corp.northstar.io",
    "debian-app-01.corp.northstar.io",
    "freebsd-build-01.corp.northstar.io",
    "win11-ws-01.corp.northstar.io",
    "macos-studio-01.corp.northstar.io",
]

# Profile bodies are REAL for their engine (a Puppet manifest, a Salt state, a
# DSC resource list) rather than filler: the profiles page shows the engine
# column and the edit dialog shows the body, so a plausible body is what makes
# the screenshot read like the product instead of a mock.
PROFILES = [  # (name, engine, description, version, active, content)
    (
        "baseline-hardening", "ansible-core",
        "CIS-aligned SSH and sysctl baseline for Linux servers.", 4, True,
        "- name: Harden SSH\n  hosts: all\n  become: true\n  tasks:\n"
        "    - name: Disable root login\n      lineinfile:\n"
        "        path: /etc/ssh/sshd_config\n"
        "        line: 'PermitRootLogin no'\n"
        "    - name: Enforce SSH idle timeout\n      lineinfile:\n"
        "        path: /etc/ssh/sshd_config\n"
        "        line: 'ClientAliveInterval 300'\n",
    ),
    (
        "nginx-web-tier", "puppet",
        "nginx package, service and vhost for the web tier.", 2, True,
        "class nginx_web_tier {\n"
        "  package { 'nginx': ensure => '1.24.0-1' }\n"
        "  service { 'nginx': ensure => running, enable => true }\n"
        "  file { '/etc/nginx/conf.d/app.conf':\n"
        "    ensure => file, mode => '0640',\n"
        "    notify => Service['nginx'],\n  }\n}\n",
    ),
    (
        "postgres-tuning", "salt",
        "Shared-buffer and connection tuning for database hosts.", 1, True,
        "postgresql-conf:\n  file.managed:\n"
        "    - name: /var/lib/pgsql/data/postgresql.conf\n"
        "    - mode: '0600'\n    - user: postgres\n"
        "postgresql-service:\n  service.running:\n"
        "    - name: postgresql\n    - enable: True\n"
        "    - watch:\n      - file: postgresql-conf\n",
    ),
    (
        "workstation-policy", "dsc",
        "Windows workstation audit and firewall policy.", 3, True,
        '[{"resource": "Registry", "valueName": "EnableFirewall",'
        ' "valueData": "1"},\n'
        ' {"resource": "Service", "name": "MpsSvc", "state": "Running"}]\n',
    ),
    (
        "legacy-chef-bootstrap", "chef",
        "Retired: superseded by baseline-hardening.", 2, False,
        "package 'ntp' do\n  action :install\nend\n",
    ),
]

# A scheduled check-mode assignment is what PRODUCES drift findings in the
# product, so seeding findings without one would show an effect with no cause.
ASSIGNMENTS = [  # (profile, fqdn, cron, check_mode)
    ("baseline-hardening", "debian-app-01.corp.northstar.io", "0 3 * * *", True),
    ("nginx-web-tier", "ubuntu-web-01.corp.northstar.io", "0 4 * * *", True),
    ("postgres-tuning", "rhel-db-01.corp.northstar.io", "30 2 * * *", True),
    ("workstation-policy", "win11-ws-01.corp.northstar.io", None, False),
]

# Drift is only interesting with AGE on it -- the dashboard's headline column
# is "drifting for N days" and its sort is longest-first, so findings all
# created "now" would render an identical, meaningless zero. rhel-db-01 is the
# oldest deliberately: it becomes row 1, which is the row the baseline-diff
# screenshot opens.
FINDINGS = [  # (fqdn, profile, task_name, detail, days_drifting)
    ("rhel-db-01.corp.northstar.io", "postgres-tuning", "postgresql-conf",
     "would change mode 0644 -> 0600 on "
     "/var/lib/pgsql/data/postgresql.conf", 23),
    ("rhel-db-01.corp.northstar.io", "postgres-tuning", "postgresql-service",
     "service postgresql is enabled but not running", 23),
    ("ubuntu-web-01.corp.northstar.io", "nginx-web-tier",
     "File[/etc/nginx/conf.d/app.conf]", "would change mode 0644 -> 0640", 9),
    ("ubuntu-web-01.corp.northstar.io", "nginx-web-tier", "Package[nginx]",
     "would change version 1.22.1-1 -> 1.24.0-1", 9),
    ("debian-app-01.corp.northstar.io", "baseline-hardening",
     "Enforce SSH idle timeout",
     "would add ClientAliveInterval 300 to /etc/ssh/sshd_config", 4),
    ("win11-ws-01.corp.northstar.io", "workstation-policy",
     "Registry[EnableFirewall]", "would change EnableFirewall 0 -> 1", 1),
]


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _seed_profiles(session, now):
    """Insert the profiles and their version history; return {name: profile}."""
    profiles = {}
    for name, engine, desc, ver, active, content in PROFILES:
        # The id is generated HERE, not left to the column default: a column
        # default is applied at INSERT, so profile.id is still None while the
        # version rows below are built and every one of them would be written
        # with a NULL profile_id (a NOT NULL violation, mid-seed).
        profile_id = uuid.uuid4()
        profile = ConfigProfile(
            id=profile_id,
            name=name, description=desc, engine=engine, content=content,
            version=ver, is_active=active,
            created_by=AUTHOR, updated_by=AUTHOR,
            created_at=now - timedelta(days=45),
            updated_at=now - timedelta(days=(2 if active else 60)),
        )
        session.add(profile)
        profiles[name] = profile
        # Every version up to the current one: a profile at version 4 with a
        # single stored version makes the restore UI look broken, not empty.
        for rev in range(1, ver + 1):
            session.add(ConfigProfileVersion(
                profile_id=profile_id, version=rev, engine=engine,
                content=content, created_by=AUTHOR,
                created_at=now - timedelta(days=45 - (rev * 8)),
            ))
    return profiles


def main():
    session = sessionmaker(bind=db.get_engine())()
    now = _now()
    try:
        hosts = {
            h.fqdn: h
            for h in session.query(Host).filter(Host.fqdn.in_(DEMO_FQDNS)).all()
        }
        if not hosts:
            print("  no demo hosts present — run make screenshots-seed first")
            return

        # Findings and versions hang off config_profile, so they go first.
        for model in (ConfigDriftFinding, ConfigProfileAssignment,
                      ConfigProfileVersion, ConfigProfile):
            session.query(model).delete()

        profiles = _seed_profiles(session, now)
        session.flush()

        assigned = 0
        for pname, fqdn, cron, check_only in ASSIGNMENTS:
            host = hosts.get(fqdn)
            if host is None or pname not in profiles:
                continue
            session.add(ConfigProfileAssignment(
                profile_id=profiles[pname].id, host_id=host.id,
                enabled=True, schedule=cron, check_mode=check_only,
                created_by=AUTHOR, created_at=now - timedelta(days=30),
                last_applied_at=now - timedelta(hours=6),
            ))
            assigned += 1

        drifting = 0
        for fqdn, pname, task, detail, days in FINDINGS:
            host = hosts.get(fqdn)
            profile = profiles.get(pname)
            if host is None or profile is None:
                continue
            # A REAL profile_id, because the dashboard's remediate action
            # re-applies that profile; a null one renders a dashboard whose
            # only action button does nothing.
            session.add(ConfigDriftFinding(
                host_id=host.id, profile_id=profile.id, profile_name=pname,
                task_name=task, detail=detail,
                first_seen_at=now - timedelta(days=days),
                # Last observed on the most recent nightly check-mode run, not
                # at first_seen: the gap between the two is what "still
                # drifting" means.
                last_seen_at=now - timedelta(hours=6),
                resolved_at=None,
            ))
            drifting += 1

        session.commit()
        print(f"    profiles: {len(profiles)} "
              f"({sum(1 for p in PROFILES if p[4])} active)")
        print(f"    assignments: {assigned}")
        print(f"    drift: {drifting} open findings")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
