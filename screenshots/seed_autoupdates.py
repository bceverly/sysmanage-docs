#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Seed Automatic Updates demo data (ROADMAP 26.1) -- through the REAL path.

Runs INSIDE the screenshot VM against the sysmanage ORM, like the other
seeders.  Apply via:  make screenshots-autoupdates-seed

Every run on screen is one the product decided: the policies are fired with
the licensed automation_engine's planner (``auto_update_runner.fire_profile``),
and the agents' answers go through the real ``update_apply_result`` handler,
so which policy a host follows, what was applied, what was left out and why,
and whether the host rebooted are the product's own verdicts.

WHAT IT HAS TO SHOW
-------------------
  * Three policies: nightly security on the production tag (reboot when
    needed, kernels excluded), a weekly one listing the database host by name
    and ON HOLD for a change freeze, and "everything" on the staging tag.
  * A host that follows the more specific policy (the database host), and a
    host opted out (the lobby kiosk).
  * Runs: one that applied everything and rebooted and came back, one that
    partly failed with apt's own error, one skipped because the host is opted
    out, a held package left out.
  * Also a "New device on the network" alert rule, for the Alerting page.
  * Maintenance windows and waiting periods: screenshots-seed gives every
    host the "Nightly Patching" window (02:00-04:00 UTC) and a weekend
    blackout, and automatic runs start only inside a window, so the policies
    fire at 02:05 UTC on the most recent weekday.  Afterwards the nightly
    policy waits 7 days for regular patches and 0 for critical ones, so the
    web host's card lists when each remaining update becomes eligible.

Run AFTER screenshots-seed (demo hosts and their pending updates).
Idempotent: removes its own rows first.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from sqlalchemy.orm import sessionmaker

from backend.persistence import db
from backend.persistence import models

ENGINE = "automation_engine"
WEB = "ubuntu-web-01.corp.northstar.io"
DB_HOST = "rhel-db-01.corp.northstar.io"
APP = "debian-app-01.corp.northstar.io"
KIOSK = "win11-ws-01.corp.northstar.io"

NIGHTLY = "Nightly security - production"
WEEKLY_DB = "Database hosts - weekly"
STAGING = "Staging - everything"
NEW_DEVICE_RULE = "New device on the network"
ROLLOUT = "Builds, desktops, then the rest - fleet by fleet"
BUILD_HOST = "freebsd-build-01.corp.northstar.io"


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _inside_window():
    """02:05 UTC on the most recent weekday: inside the demo "Nightly
    Patching" window and outside the weekend blackout (seed.py)."""
    now = _now()
    at = now.replace(hour=2, minute=5, second=0, microsecond=0)
    while at >= now or at.weekday() >= 5:
        at -= timedelta(days=1)
    return at


async def _boot_engine():
    from backend.licensing.license_service import license_service  # noqa: PLC0415
    from backend.licensing.module_loader import module_loader  # noqa: PLC0415

    await license_service.initialize()
    module_loader.initialize()
    if not await module_loader.ensure_module_available(ENGINE):
        raise SystemExit(f"{ENGINE} is not available -- is this the Enterprise VM?")
    return module_loader.get_module(ENGINE)


def _tag(session, name):
    tag = session.query(models.Tag).filter(models.Tag.name == name).first()
    if tag is None:
        raise SystemExit(f"tag {name!r} missing -- run screenshots-seed first")
    return tag


def _clear(session):
    names = (NIGHTLY, WEEKLY_DB, STAGING, ROLLOUT)
    ids = [p.id for p in session.query(models.UpgradeProfile).filter(
        models.UpgradeProfile.name.in_(names))]  # fmt: skip
    session.query(models.AutoUpdateRun).delete()
    session.query(models.AutoUpdateRollout).delete()
    if ids:
        session.query(models.UpgradeProfileRolloutStage).filter(
            models.UpgradeProfileRolloutStage.profile_id.in_(ids)
        ).delete()
    session.query(models.UpdateExecutionLog).filter(
        models.UpdateExecutionLog.execution_method == "automatic"
    ).delete()
    if ids:
        session.query(models.UpgradeProfileHost).filter(
            models.UpgradeProfileHost.profile_id.in_(ids)
        ).delete()
        session.query(models.UpgradeProfile).filter(
            models.UpgradeProfile.id.in_(ids)
        ).delete()
    session.query(models.AutoUpdateSettings).delete()
    session.query(models.AlertRule).filter(models.AlertRule.name == NEW_DEVICE_RULE).delete()
    for host in session.query(models.Host):
        host.auto_update_opt_out, host.auto_update_opt_out_reason = False, None


# Applying updates deletes them (the real result handler does), so a second
# run would find nothing to plan.  The first run keeps the demo hosts' updates
# as they came from seed.py; every run starts from that copy.
# Root-owned, unlike /var/tmp: the seed runs as root, and a fixed name in a
# world-writable directory could be a symlink planted to make it overwrite
# something else (CWE-61).  /var/lib/sysmanage exists on every server VM.
BASELINE = "/var/lib/sysmanage/seed_autoupdates_baseline.json"


def _restore_updates(session, hosts):
    """Put the demo hosts' package updates back as seed.py left them."""
    columns = [c.name for c in models.PackageUpdate.__table__.columns]
    host_ids = [h.id for h in hosts]
    query = session.query(models.PackageUpdate).filter(
        models.PackageUpdate.host_id.in_(host_ids)
    )
    if not os.path.exists(BASELINE):
        rows = [{c: getattr(r, c) for c in columns} for r in query]
        with open(BASELINE, "w", encoding="utf-8") as handle:
            json.dump(rows, handle, default=str)
        return
    with open(BASELINE, encoding="utf-8") as handle:
        rows = json.load(handle)
    query.delete(synchronize_session=False)
    session.flush()
    for row in rows:
        values = {c: row.get(c) for c in columns}
        for key in ("discovered_at", "created_at", "updated_at"):
            if values.get(key):
                values[key] = datetime.fromisoformat(values[key])
        session.add(models.PackageUpdate(**values))
    session.flush()


def _policies(session, hosts):
    now = _now()
    nightly = models.UpgradeProfile(
        name=NIGHTLY, description="Security fixes every night; kernels by hand",
        cron="0 3 * * *", enabled=True, auto_apply=True, security_only=True,
        staggered_window_min=30, tag_id=_tag(session, "production").id,
        reboot_mode="when_needed", excluded_packages="linux-image-*, kernel*",
        next_run=now + timedelta(hours=6),
    )  # fmt: skip
    weekly = models.UpgradeProfile(
        name=WEEKLY_DB, description="The database host, Sunday mornings",
        cron="0 6 * * 0", enabled=True, auto_apply=True, security_only=False,
        reboot_mode="never", require_backup_hours=24, held=True,
        hold_reason="Quarter-end freeze until Dec 1", hold_by="admin@northstar.io",
        hold_at=now - timedelta(days=2), next_run=now + timedelta(days=3),
    )  # fmt: skip
    staging = models.UpgradeProfile(
        name=STAGING, description="Everything, so production sees it a week later",
        cron="0 2 * * *", enabled=True, auto_apply=True, security_only=False,
        tag_id=_tag(session, "staging").id, reboot_mode="when_needed",
        next_run=now + timedelta(hours=5),
    )  # fmt: skip
    session.add_all([nightly, weekly, staging])
    session.flush()
    session.add(models.UpgradeProfileHost(profile_id=weekly.id, host_id=hosts[DB_HOST].id))
    kiosk = hosts[KIOSK]
    kiosk.auto_update_opt_out = True
    kiosk.auto_update_opt_out_reason = "Lobby kiosk; the vendor patches it"
    return nightly, staging


UPDATE_COMMANDS = ("apply_updates", "check_updates", "reboot_system")


def _advertise(host):
    """Add the update commands to the host's EXISTING capability report (as
    seed_discovery does for discovery): the server refuses to queue a command
    a host's agent does not advertise, and skips that host's run."""
    report = json.loads(host.agent_capabilities) if host.agent_capabilities else None
    if not isinstance(report, dict) or not isinstance(report.get("commands"), list):
        return  # no report at all: the server sends anything
    for command in UPDATE_COMMANDS:
        if command not in report["commands"]:
            report["commands"].append(command)
    host.agent_capabilities = json.dumps(report)


def _backdate_updates(session, hosts, before):
    """The runs are planned at ``before`` (inside last night's window), but
    seed.py discovered the updates just now -- and an update is not eligible
    until after it was discovered.  Say they were found days earlier."""
    found = before - timedelta(days=3)
    for host in hosts:
        for row in session.query(models.PackageUpdate).filter(
            models.PackageUpdate.host_id == host.id
        ):
            row.discovered_at = found


def _hold_one_package(session, host):
    """What the agent reports for a package pinned with apt-mark hold."""
    row = (
        session.query(models.PackageUpdate)
        .filter(models.PackageUpdate.host_id == host.id,
                models.PackageUpdate.package_name == "sudo")
        .first()
    )  # fmt: skip
    if row is not None:
        row.held = True


async def _answer(session, host, applied, failed, requires_reboot):
    """The agent's update_apply_result, through the real handler."""
    from backend.api.update_handlers import (  # noqa: PLC0415
        handle_update_apply_result,
    )

    connection = SimpleNamespace(host_id=host.id, is_mock_connection=True)
    await handle_update_apply_result(
        session,
        connection,
        {
            "hostname": host.fqdn,
            "updated_packages": [{"package_name": n, "package_manager": m} for n, m in applied],
            "failed_packages": [
                {"package_name": n, "package_manager": m, "error": e} for n, m, e in failed
            ],
            "requires_reboot": requires_reboot,
        },
    )


def _planned(session, host):
    run = session.query(models.AutoUpdateRun).filter(
        models.AutoUpdateRun.host_id == host.id,
        models.AutoUpdateRun.status == "queued",
    ).one()
    return [(p["package_name"], p["package_manager"]) for p in run.packages]


def _rollout_policy(session):
    """Fleet by fleet (26.4): the build host is the canary, then the desktops,
    then everything else.  Every host, so nothing is left out of a fleet."""
    policy = models.UpgradeProfile(
        name=ROLLOUT, description="One fleet at a time; the build host first",
        cron="0 4 * * 2", enabled=True, auto_apply=True, security_only=False,
        reboot_mode="never", rollout_enabled=True, rollout_max_failure_pct=0,
        next_run=_now() + timedelta(days=4),
    )  # fmt: skip
    session.add(policy)
    session.flush()
    for position, (name, tag, soak) in enumerate(
        (("Canary fleet", "build", 24 * 60), ("Desktops", "desktop", 4 * 60))
    ):
        session.add(models.UpgradeProfileRolloutStage(
            profile_id=policy.id, position=position, name=name,
            tag_id=_tag(session, tag).id, soak_minutes=soak,
        ))  # fmt: skip
    session.flush()
    return policy


def _run_rollout(session, eng, policy, hosts, now):
    """Start the rollout as a person's Trigger Now would; when the canary got
    updates, its run fails and the health gate halts the rollout -- the
    Rollouts card then shows the halt, its reason and the host, with Resume
    and Cancel.  With nothing to apply the canary soaks instead."""
    from backend.services import (  # noqa: PLC0415
        auto_update_rollout,
        auto_update_runner,
    )

    print("  rollout:", auto_update_runner.fire_profile(
        session, eng, policy, now, triggered_by="admin@northstar.io"))  # fmt: skip
    session.commit()
    build = hosts[BUILD_HOST]
    queued = session.query(models.AutoUpdateRun).filter(
        models.AutoUpdateRun.host_id == build.id,
        models.AutoUpdateRun.status == "queued",
    ).first()
    if queued is not None:
        failed = [(p["package_name"], p["package_manager"],
                   "pkg: Cannot get an advisory lock on a database, it is locked by another process")
                  for p in queued.packages]  # fmt: skip
        asyncio.run(_answer(session, build, [], failed, False))
        session.commit()
    auto_update_rollout.advance_rollouts(session, eng, now + timedelta(minutes=2))
    session.commit()
    for rollout in session.query(models.AutoUpdateRollout):
        print(f"  rollout {rollout.profile_name}: {rollout.status} {rollout.halt_reason or ''}")


def _alert_rule(session):
    session.add(
        models.AlertRule(
            name=NEW_DEVICE_RULE,
            description="An email the first time an unknown device appears",
            condition_type="new_network_device",
            condition_params={"device_types": ["computer", "phone_or_tablet", "iot", "unknown"],
                              "settle_minutes": 5, "new_address": False,
                              "ignore_randomized": False},  # fmt: skip
            severity="medium", enabled=True, cooldown_minutes=0, host_filter={},
        )
    )  # fmt: skip


def main():
    session = sessionmaker(bind=db.get_engine())()
    eng = asyncio.run(_boot_engine())
    from backend.services import (  # noqa: PLC0415
        auto_update_results,
        auto_update_runner,
    )

    try:
        hosts = {h.fqdn: h for h in session.query(models.Host)}
        missing = [f for f in (WEB, DB_HOST, APP, KIOSK, BUILD_HOST) if f not in hosts]
        if missing:
            raise SystemExit(f"demo hosts missing ({missing}) -- run screenshots-seed first")
        _clear(session)
        for fqdn in (WEB, DB_HOST, APP, KIOSK, BUILD_HOST):
            _advertise(hosts[fqdn])
        session.commit()
        now = _inside_window()
        demo = [hosts[f] for f in (WEB, DB_HOST, APP, KIOSK, BUILD_HOST)]
        _restore_updates(session, demo)
        _backdate_updates(session, demo, now)
        nightly, staging = _policies(session, hosts)
        _hold_one_package(session, hosts[WEB])
        auto_update_runner.settings_row(session)
        _alert_rule(session)
        session.commit()

        print("  nightly:", auto_update_runner.fire_profile(session, eng, nightly, now))
        print("  staging:", auto_update_runner.fire_profile(session, eng, staging, now))
        session.commit()

        web, app = hosts[WEB], hosts[APP]
        # The web host applies everything it was sent and needs a reboot.
        asyncio.run(_answer(session, web, _planned(session, web), [], True))
        # The app host: one package fails with apt's own words.
        planned = _planned(session, app)
        broken = planned[-1]
        asyncio.run(_answer(
            session, app, planned[:-1],
            [(broken[0], broken[1],
              "E: Sub-process /usr/bin/dpkg returned an error code (1)")],
            False,
        ))  # fmt: skip
        session.commit()

        # The web host came back from its reboot.
        session.expire_all()
        web = session.get(models.Host, web.id)
        web.boot_time = _now() + timedelta(minutes=2)
        session.commit()
        auto_update_results.follow_reboots(session, eng, _now() + timedelta(minutes=3))
        session.commit()

        # Waiting periods (26.3): what is still pending on the web host now
        # waits its 7 days, and its card says until when.
        nightly = session.get(models.UpgradeProfile, nightly.id)
        nightly.wait_days_regular, nightly.wait_days_critical = 7, 0
        session.commit()

        # Fleet by fleet (26.4): the Rollouts card and the fleets editor.
        rollout = _rollout_policy(session)
        session.commit()
        _run_rollout(session, eng, rollout, hosts, _inside_window())

        for run in session.query(models.AutoUpdateRun).order_by(models.AutoUpdateRun.queued_at):
            host = session.get(models.Host, run.host_id)
            print(f"  run {host.fqdn}: {run.status} {run.reason or ''} "
                  f"applied={run.applied_count} failed={run.failed_count} "
                  f"reboot={run.reboot_status}")  # fmt: skip
    finally:
        session.close()


if __name__ == "__main__":
    main()
