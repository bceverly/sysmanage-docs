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
                              + config_inventory (+ members) + config_job_template
                              + config_job (+ targets) + config_remediation_rule

Run AFTER make screenshots-seed (demo hosts). Idempotent: clears the rows it
manages (FK-safe order) then re-inserts.
"""
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from backend.persistence import db
from backend.persistence.models import (
    ConfigDriftFinding,
    ConfigInventory,
    ConfigInventoryMember,
    ConfigJob,
    ConfigJobTarget,
    ConfigJobTemplate,
    ConfigProfile,
    ConfigProfileAssignment,
    ConfigProfileVersion,
    ConfigRemediationRule,
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


# --- Phase 20.1 fleet jobs ---------------------------------------------------

# (name, description, all_hosts, [member fqdns])
INVENTORIES = [
    ("linux-servers", "Every managed Linux server.", False,
     ["ubuntu-web-01.corp.northstar.io", "rhel-db-01.corp.northstar.io",
      "debian-app-01.corp.northstar.io"]),
    ("web-tier", "Front-end web servers.", False,
     ["ubuntu-web-01.corp.northstar.io"]),
    ("entire-fleet", "Every active host in this tenant.", True, []),
]

# (name, profile, inventory, check_mode, concurrency, cron)
#
# The concurrencies differ on purpose: the screenshot has to show that this is
# a per-WORK setting rather than a server-wide one. A package-touching profile
# against a shared mirror wants a small number; a file-permissions sweep can
# saturate.
JOB_TEMPLATES = [
    ("nightly-hardening-check", "baseline-hardening", "linux-servers",
     True, 25, "0 2 * * *"),
    ("web-tier-enforce", "nginx-web-tier", "web-tier", False, 5, None),
    ("fleet-audit", "baseline-hardening", "entire-fleet", True, 50, "0 4 * * 0"),
]

# (template, status, total, ok, failed, skipped, hours_ago, detail)
#
# One of each interesting shape: a completed run with a handful of failures
# (which is `completed`, NOT `failed` -- the status answers "did this job do
# its work"), one still running, and one where every host declined.
JOBS = [
    ("nightly-hardening-check", "completed", 3, 2, 1, 0, 8, None),
    ("web-tier-enforce", "running", 3, 1, 0, 0, 0, None),
    ("fleet-audit", "completed", 6, 4, 0, 2, 32, None),
]

# (job template, host fqdn, status, detail)
JOB_TARGETS = {
    "nightly-hardening-check": [
        ("ubuntu-web-01.corp.northstar.io", "succeeded", None),
        ("debian-app-01.corp.northstar.io", "succeeded", None),
        ("rhel-db-01.corp.northstar.io", "failed",
         "the run reported failure"),
    ],
    "web-tier-enforce": [
        ("ubuntu-web-01.corp.northstar.io", "succeeded", None),
        ("debian-app-01.corp.northstar.io", "queued", None),
        ("rhel-db-01.corp.northstar.io", "pending", None),
    ],
    "fleet-audit": [
        ("ubuntu-web-01.corp.northstar.io", "succeeded", None),
        ("rhel-db-01.corp.northstar.io", "succeeded", None),
        ("debian-app-01.corp.northstar.io", "succeeded", None),
        ("freebsd-build-01.corp.northstar.io", "succeeded", None),
        ("win11-ws-01.corp.northstar.io", "skipped",
         "this host does not advertise config-management support"),
        ("macos-studio-01.corp.northstar.io", "skipped",
         "this host does not advertise config-management support"),
    ],
}

# (name, task pattern, repair profile, scope profile, priority, auto_apply)
#
# The list is rendered in precedence order, so the priorities are spread to
# make that visible rather than all sitting at the default.
REMEDIATION_RULES = [
    ("nginx-config-repair", "File[/etc/nginx/*]", "nginx-web-tier",
     "nginx-web-tier", 10, True),
    ("sshd-idle-timeout", "Enforce SSH idle timeout*", "baseline-hardening",
     None, 50, True),
    ("postgres-service-repair", "*postgresql*", "baseline-hardening", None,
     100, False),
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


def _seed_fleet(session, hosts, profiles, now):
    """Inventories, job templates, jobs and their per-host targets."""
    inventories = {}
    for name, desc, all_hosts, member_fqdns in INVENTORIES:
        inventory_id = uuid.uuid4()
        session.add(ConfigInventory(
            id=inventory_id, name=name, description=desc, all_hosts=all_hosts,
            created_by=AUTHOR, updated_by=AUTHOR,
            created_at=now - timedelta(days=40),
            updated_at=now - timedelta(days=12),
        ))
        inventories[name] = inventory_id
        for fqdn in member_fqdns:
            host = hosts.get(fqdn)
            if host is not None:
                session.add(ConfigInventoryMember(
                    inventory_id=inventory_id, host_id=host.id,
                    created_at=now - timedelta(days=40),
                ))
    # The job templates below carry a real inventory_id FK, and NOTHING
    # orders the two mappers: the unit of work derives flush order from
    # relationship(), not from a ForeignKey column, and ConfigJobTemplate
    # deliberately has no relationship to ConfigInventory. Without this the
    # template INSERT can reach the database first and the FK fires.
    session.flush()

    templates = {}
    for name, pname, iname, check, conc, cron in JOB_TEMPLATES:
        if pname not in profiles or iname not in inventories:
            continue
        template_id = uuid.uuid4()
        session.add(ConfigJobTemplate(
            id=template_id, name=name,
            description=f"{pname} across {iname}",
            profile_id=profiles[pname].id, inventory_id=inventories[iname],
            check_mode=check, concurrency=conc, schedule=cron, enabled=True,
            created_by=AUTHOR, updated_by=AUTHOR,
            created_at=now - timedelta(days=35),
            updated_at=now - timedelta(days=5),
            last_launched_at=now - timedelta(hours=8) if cron else None,
        ))
        templates[name] = (template_id, name, pname, iname, check, conc)
    # Same reason, and this is the one that actually bit: config_job.template_id
    # is a real FK that softens to NULL on delete, but ConfigJob carries no
    # relationship back to ConfigJobTemplate (history outlives its parents), so
    # the flush is free to write the jobs before the templates they point at.
    session.flush()

    jobs = 0
    for tname, status, total, ok, failed, skipped, hours, detail in JOBS:
        entry = templates.get(tname)
        if entry is None:
            continue
        template_id, _n, pname, iname, check, conc = entry
        job_id = uuid.uuid4()
        started = now - timedelta(hours=hours)
        session.add(ConfigJob(
            id=job_id, template_id=template_id, template_name=tname,
            profile_id=profiles[pname].id, profile_name=pname,
            inventory_name=iname, status=status, check_mode=check,
            concurrency=conc, total_targets=total, succeeded_count=ok,
            failed_count=failed, skipped_count=skipped,
            requested_by=AUTHOR if status != "completed" else None,
            detail=detail, created_at=started, started_at=started,
            # A running job has no finish time; one that finished carries the
            # real gap, so "took 4 minutes" is readable from the row.
            finished_at=None if status == "running"
            else started + timedelta(minutes=4),
        ))
        jobs += 1

        for fqdn, tstatus, tdetail in JOB_TARGETS.get(tname, []):
            host = hosts.get(fqdn)
            if host is None:
                continue
            terminal = tstatus in ("succeeded", "failed", "skipped")
            session.add(ConfigJobTarget(
                job_id=job_id, host_id=host.id, host_fqdn=fqdn,
                status=tstatus,
                command_id=str(uuid.uuid4()) if tstatus != "pending" else None,
                detail=tdetail,
                queued_at=started if tstatus != "pending" else None,
                finished_at=started + timedelta(minutes=2) if terminal else None,
            ))
    return len(inventories), len(templates), jobs


def _seed_remediation(session, profiles, now):
    """Remediation rules binding drift findings to the profiles that fix them."""
    seeded = 0
    for name, pattern, repair, scope, priority, auto in REMEDIATION_RULES:
        if repair not in profiles:
            continue
        session.add(ConfigRemediationRule(
            name=name,
            description=f"Repairs {pattern} using {repair}.",
            profile_id=profiles[scope].id if scope in profiles else None,
            task_pattern=pattern,
            remediation_profile_id=profiles[repair].id,
            enabled=True, priority=priority, auto_apply=auto,
            created_by=AUTHOR, updated_by=AUTHOR,
            created_at=now - timedelta(days=20),
            updated_at=now - timedelta(days=3),
        ))
        seeded += 1
    return seeded


def _wake_demo_hosts(session, hosts, now):
    """Make the approved demo hosts look like a live, managed fleet.

    ``resolve_hosts()`` counts only ACTIVE hosts -- correct, because queuing a
    job for a host whose agent will never answer buries the work in a queue
    the operator sees as dispatched. But the demo hosts are REST fixtures with
    no agent behind them, so the heartbeat monitor marks them down a few
    minutes after seeding, and every inventory then resolves to zero: a
    documentation screenshot that makes the feature look broken.

    So the fleet is refreshed here, in the last seed before the capture. The
    monitor only ever re-marks hosts whose status is still ``up``, so doing
    this earlier would simply be undone before the screenshots are taken.
    """
    woken = 0
    for host in hosts.values():
        if host.approval_status != "approved":
            continue
        host.status = "up"
        host.active = True
        host.last_access = now
        woken += 1
    return woken


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

        awake = _wake_demo_hosts(session, hosts, now)

        # Children before parents: targets hang off jobs, jobs and members
        # off templates and inventories, and everything above hangs off
        # config_profile.
        for model in (ConfigJobTarget, ConfigJob, ConfigJobTemplate,
                      ConfigInventoryMember, ConfigInventory,
                      ConfigRemediationRule, ConfigDriftFinding,
                      ConfigProfileAssignment, ConfigProfileVersion,
                      ConfigProfile):
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

        inv_n, tpl_n, job_n = _seed_fleet(session, hosts, profiles, now)
        rule_n = _seed_remediation(session, profiles, now)

        session.commit()
        print(f"    inventories: {inv_n}  templates: {tpl_n}  jobs: {job_n}")
        print(f"    remediation rules: {rule_n}")
        print(f"    profiles: {len(profiles)} "
              f"({sum(1 for p in PROFILES if p[4])} active)")
        print(f"    assignments: {assigned}")
        print(f"    drift: {drifting} open findings")
        print(f"    demo hosts marked up/active: {awake}")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
