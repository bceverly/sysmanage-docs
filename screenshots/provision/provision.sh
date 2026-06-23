#!/usr/bin/env bash
# Provision a clean Ubuntu VM with a running SysManage server + agent for taking
# documentation screenshots. Runs as root inside the Vagrant VM.
#
# This wraps the project's OWN install mechanism rather than reinventing it, so it
# tracks the real installer over time. The stages marked [VERIFY] are the ones to
# confirm against the current install flow on the first real run — they invoke
# project scripts whose exact names/flags may evolve.
#
# Env in:  SYSMANAGE_ADMIN_PW  (admin password for the seeded instance)
set -euo pipefail

SRC=/srv/src
SERVER=/opt/sysmanage
AGENT=/opt/sysmanage-agent
ADMIN_USER="admin@sysmanage.org"
ADMIN_PW="${SYSMANAGE_ADMIN_PW:-ChangeMe-Dev-Only!}"

echo "=== [1/7] OS dependencies ==="
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y postgresql postgresql-contrib python3 python3-venv python3-pip \
    gettext build-essential libpq-dev git rsync curl jq ca-certificates gnupg
# The web UI is React + Vite, which needs Node 18+. Ubuntu's default 'nodejs' is
# Node 12 — Vite crashes on its optional-chaining call syntax (enableCompileCache?.()).
# Pull Node 20 LTS from NodeSource (provides a matching npm) unless it's already current.
if ! node --version 2>/dev/null | grep -qE '^v(1[89]|2[0-9])\.'; then
    echo "Installing Node 20 LTS from NodeSource..."
    # Purge the distro Node 12 stack first: its libnode-dev ships headers
    # (/usr/include/node/common.gypi) that collide with NodeSource's nodejs
    # package and abort the dpkg unpack with an "overwrite" error.
    apt-get purge -y libnode-dev libnode72 nodejs npm >/dev/null 2>&1 || true
    apt-get autoremove -y >/dev/null 2>&1 || true
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    # --force-overwrite is a belt-and-suspenders guard against any remaining
    # distro-vs-NodeSource file collisions.
    apt-get install -y -o Dpkg::Options::="--force-overwrite" nodejs
fi

echo "=== [2/7] copy working copies into /opt (never mutate the synced source) ==="
# On a RE-provision the previous stack is still running; its Vite dev server
# keeps writing into frontend/node_modules/.vite, which races the 'rm -rf'
# below and aborts it with "Directory not empty". Stop the old stack (and kill
# any stragglers holding files) before removing the trees so re-provisioning an
# existing box works, not just a fresh one.
if [ -d "$SERVER" ]; then ( cd "$SERVER" && make stop >/dev/null 2>&1 ) || true; fi
pkill -f 'vite' 2>/dev/null || true
pkill -f '/opt/sysmanage' 2>/dev/null || true
sleep 2
rm -rf "$SERVER" "$AGENT"
cp -a "$SRC/sysmanage" "$SERVER"
cp -a "$SRC/sysmanage-agent" "$AGENT"

echo "=== [3/7] PostgreSQL: role + database ==="
systemctl enable --now postgresql
# Run from /tmp: the provisioner's CWD is /home/vagrant, which the postgres user
# can't enter, and psql prints a "could not change directory" warning otherwise.
cd /tmp
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='sysmanage'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE ROLE sysmanage LOGIN PASSWORD 'sysmanage';"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='sysmanage'" | grep -q 1 || \
    sudo -u postgres createdb -O sysmanage sysmanage

echo "=== [4/7] server config (/etc/sysmanage.yaml) ==="
# Self-referencing, HTTP dev mode so no certs are needed for screenshots.
#
# Two deliberate choices to avoid the red "Configuration Security Warning" banner
# (backend/api/security.py checks for these):
#   * NO security.admin_userid / admin_password — leaving default admin creds in the
#     YAML trips the banner. The admin user is instead created directly in stage [5]
#     via create_admin_user(), so the YAML creds aren't needed.
#   * email.enabled: true with smtp.host=localhost — the email service treats
#     "localhost" as configured without credentials, so email is "on" for the UI
#     (it doesn't need to actually send for screenshots).
cat > /etc/sysmanage.yaml <<YAML
registry:
  host: localhost
  port: 5432
  user: sysmanage
  password: sysmanage
  name: sysmanage
api:
  host: 0.0.0.0
  port: 8080
webui:
  host: 0.0.0.0
  port: 3000
  ssl: false
  https: false
security:
  jwt_secret: "dev-screenshot-secret-not-for-production"
email:
  enabled: true
  smtp:
    host: localhost
    port: 25
    use_tls: false
    use_ssl: false
    username: ""
    password: ""
    timeout: 30
  from_address: noreply@demo.sysmanage.org
  from_name: SysManage Demo
  templates:
    subject_prefix: "[SysManage]"
# PRIVACY: disable server-side GeoIP entirely. The server otherwise geolocates the
# public IP an agent reports (and the VM's own real agent would report the
# operator's real WAN IP), which would put a real home location on the /map view.
# With this off, NO IP is ever resolved; the demo map markers come solely from the
# fake coordinates seed_geo.sql writes directly into the host rows.
geo_lookup:
  enabled: false
YAML

echo "=== [5/7] install + migrate the server ==="
cd "$SERVER"
make setup-venv
# setup-venv only creates the venv + pip; the project's Python dependencies
# (alembic, fastapi, sqlalchemy, ...) must be installed before migrating/serving.
echo "Installing Python dependencies (a few minutes)..."
.venv/bin/pip install -r requirements.txt
# [VERIFY] OpenBAO bring-up + DB migration. `make migrate` runs the migration
# chain; on a multitenancy-enabled build this also needs OpenBAO running. For the
# OSS/collapsed screenshot build, the default single-DB path applies.
make migrate || { echo "migrate failed — check deps / OpenBAO / DB config"; exit 1; }

# Initial admin user. The secure installer (scripts/_sysmanage_secure_installation.py)
# only creates this interactively, so we call its create_admin_user() directly with
# the four keys it actually reads (email/password/first_name/last_name); 'email'
# becomes the login userid. On a re-provision the user already exists and the insert
# fails the unique constraint — harmless, the '|| echo' swallows it.
.venv/bin/python - <<PY || echo "NOTE: admin user already exists (re-provision) or create-admin hook changed"
import sys
sys.path.insert(0, ".")
from scripts._sysmanage_secure_installation import create_admin_user
create_admin_user(
    {
        "email": "${ADMIN_USER}",
        "password": "${ADMIN_PW}",
        "first_name": "Admin",
        "last_name": "User",
    },
    salt=None,
)
PY

echo "=== [6/7] start the server (backend + frontend) ==="
# [VERIFY] `make start` launches backend + frontend (+ OpenBAO). For a headless VM
# it must run detached; adjust to the project's service/daemon mechanism.
nohup make start > /var/log/sysmanage-start.log 2>&1 &
sleep 30
curl -fsS http://localhost:8080/api/health >/dev/null 2>&1 && echo "backend up" || echo "backend not responding yet (see /var/log/sysmanage-start.log)"

echo "=== [7/7] configure + start the agent (gives one real, fully-populated host) ==="
cat > "$AGENT/sysmanage-agent.yaml" <<YAML
server:
  hostname: "127.0.0.1"
  port: 8080
  use_https: false
  verify_ssl: false
YAML
cd "$AGENT"
[ -f Makefile ] && make setup-venv 2>/dev/null || python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt 2>/dev/null || true
nohup ./.venv/bin/python main.py > /var/log/sysmanage-agent.log 2>&1 &

# ---- Licensed tiers (opt-in: SYSMANAGE_PRO=1, SYSMANAGE_TIER=professional|enterprise)
# Install the tier's Cython engines from the PREBUILT, versioned bundles the Pro+
# repo already ships (storage/modules/<code>/<ver>/<plat>/<arch>/<py>/<code>.tar.gz),
# drop in a self-signed license for that tier, and verify the engines load. We do
# NOT compile anything: a matching linux/x86_64/<py> bundle already exists for every
# engine, so building would just waste minutes AND drag in deadsnakes +
# python3.11..3.14 (build-modules-force loops every installed Python). The engine
# list + license modules/features are DERIVED from the tier (get_modules_for_tier /
# get_features_for_tier), so professional installs the Pro engines and enterprise
# installs the full Enterprise set. The box is LEFT licensed so the matching capture
# pass runs against loaded engines; the OSS shots come from the separate, never-
# licensed `make screenshots` run.
if [ "${SYSMANAGE_PRO:-0}" = "1" ]; then
    PRO=/srv/src/sysmanage-professional-plus
    SVPY=/opt/sysmanage/.venv/bin/python
    MODDIR=/var/lib/sysmanage/modules
    LICDIR=/var/lib/sysmanage/license
    # The server venv's Python ABI — the ONLY version we install engines for.
    PYVER="$("$SVPY" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
    PLAT=linux; ARCH=x86_64
    # License tier to grant: professional | enterprise (default professional).
    TIER="${SYSMANAGE_TIER:-professional}"
    if [ ! -d "$PRO" ]; then
        echo "PRO: $PRO not synced — run with SYSMANAGE_PRO=1 set before 'vagrant up'"; exit 1
    fi
    # Engines to install = exactly the modules this tier's license grants (derived
    # from the canonical signing-side definitions, minus proplus_core which is a
    # frontend plugin bundle handled separately). A professional build installs the
    # Pro engines; an enterprise build installs the full Enterprise set (federation,
    # air-gap, virtualization, observability, fleet, automation, IdP, mirroring, ...).
    ENGINES="$(PYTHONPATH="$PRO" "$SVPY" -c "from backend.licensing.features import get_modules_for_tier; print(' '.join(m for m in get_modules_for_tier('$TIER') if m != 'proplus_core'))")"
    if [ -z "$ENGINES" ]; then
        echo "PRO: could not resolve engine list for tier '$TIER'"; exit 1
    fi

    echo "=== [PRO 1/4] install prebuilt $TIER engines ($PLAT/$ARCH/$PYVER, NO compile) ==="
    mkdir -p "$MODDIR" "$LICDIR"
    for code in $ENGINES; do
        # Highest version that has a bundle for THIS Python ABI (sort -V on the
        # version dir, which is the 3rd path component under the module).
        # ``|| true``: with set -e + pipefail, a no-match ls would otherwise abort
        # the whole provision on the command substitution before the -z check.
        tb="$(ls -1 "$PRO"/storage/modules/"$code"/*/"$PLAT"/"$ARCH"/"$PYVER"/"$code".tar.gz 2>/dev/null \
              | sort -V | tail -1 || true)"
        if [ -z "$tb" ]; then
            echo "  WARN: no $PLAT/$ARCH/$PYVER bundle for $code — skipping (engine will not load)"
            continue
        fi
        # Extract into the same per-version layout module_loader produces, so the
        # engine's locales/ sit beside its .so for i18n binding.
        dest="$MODDIR/${code}_${PYVER}"
        rm -rf "$dest"; mkdir -p "$dest"
        tar -xzf "$tb" -C "$dest"
        # version dir is 4 levels up from the tarball: <ver>/<plat>/<arch>/<py>/<code>.tar.gz
        ver="$(basename "$(dirname "$(dirname "$(dirname "$(dirname "$tb")")")")")"
        echo "  $code v$ver"
    done

    # Frontend plugin bundles (IIFE JS): the Pro+ UI pages render from these. The
    # plugin loader / serving endpoint (backend/api/plugin_bundle.py) is a pure
    # filesystem glob of <modules_path>/*-plugin.iife.js — no DB row, no download,
    # no per-file license check — so we just drop the highest-version bundle for
    # each licensed module (engines + proplus_core) plus the top-level proplus
    # bootstrap into place. Architecture/Python-independent (it's browser JS).
    # NOTE: several Enterprise engines (virtualization, observability,
    # repository_mirroring, external_idp, both air-gap, federation_site) ship NO
    # frontend plugin bundle — their UI is OSS-native (host-detail tabs / Settings
    # tabs gated on the engine being licensed), so a missing plugin here is normal.
    echo "  + frontend plugin bundles:"
    for code in $ENGINES proplus_core; do
        # ``|| true`` so a no-match ls doesn't abort provisioning (set -e + pipefail).
        pj="$(ls -1 "$PRO"/storage/modules/"$code"/*/"$code"-plugin.iife.js 2>/dev/null \
              | sort -V | tail -1 || true)"
        if [ -z "$pj" ]; then
            echo "    (no plugin bundle for $code — OSS-native UI or none)"
            continue
        fi
        cp -f "$pj" "$MODDIR/${code}-plugin.iife.js"
        echo "    ${code}-plugin.iife.js"
    done
    # NOTE: do NOT copy the top-level storage/modules/proplus-plugin.iife.js.
    # It is a LEGACY monolithic bundle that re-registers a subset of the
    # contributions (health host-tab, vulnerabilities nav, CVE Database +
    # License settings tabs, compliance nav) that the per-engine bundles above
    # already provide. Shipping both double-registers those items, producing
    # duplicate menu entries / tabs. The per-engine bundles are the complete,
    # current set, so this file is pure overlap and is intentionally skipped.
    rm -f "$MODDIR/proplus-plugin.iife.js"

    echo "=== [PRO 2/4] register engines in proplus_module_cache (offline; no license server) ==="
    # The loader resolves each licensed engine through the proplus_module_cache
    # table; with no row it would try to download from the license server (which
    # this box has no URL for). Upsert one row per extracted engine .so so the
    # loader finds them locally on startup — the same trick the air-gap overlay
    # installer uses.
    cd /opt/sysmanage && PYTHONPATH=/opt/sysmanage "$SVPY" - <<'PY'
import hashlib, json, platform
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from backend.persistence import db
from backend.persistence.models import ProPlusModuleCache

MODULES_DIR = Path("/var/lib/sysmanage/modules")
SYSTEM = platform.system().lower()
MACHINE = {"x86_64": "x86_64", "amd64": "x86_64",
           "aarch64": "aarch64", "arm64": "aarch64"}.get(
    platform.machine().lower(), platform.machine().lower())


def sha512(path):
    h = hashlib.sha512()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


Session = sessionmaker(bind=db.get_engine())
now = datetime.now(timezone.utc).replace(tzinfo=None)
inserted = updated = 0
with Session() as s:
    # Per-engine dirs are named "<code>_<pyver>" (e.g. health_engine_3.10).
    for d in sorted(MODULES_DIR.glob("*_[0-9].[0-9]*")):
        if not d.is_dir():
            continue
        pyv = d.name.rsplit("_", 1)[1]
        code = d.name[: -(len(pyv) + 1)]
        sos = sorted(d.glob("*.so"))
        if not sos:
            print(f"  no .so in {d}")
            continue
        so = sos[0]
        try:
            ver = json.loads((d / "metadata.json").read_text())["version"]
        except Exception:
            ver = "unknown"
        digest = sha512(so)
        row = (s.query(ProPlusModuleCache)
               .filter_by(module_code=code, platform=SYSTEM,
                          architecture=MACHINE, python_version=pyv)
               .first())
        if row is None:
            s.add(ProPlusModuleCache(
                module_code=code, version=ver, platform=SYSTEM,
                architecture=MACHINE, python_version=pyv,
                file_path=str(so), file_hash=digest, downloaded_at=now))
            inserted += 1
        else:
            row.version = ver
            row.file_path = str(so)
            row.file_hash = digest
            row.downloaded_at = now
            updated += 1
    s.commit()
print(f"  module cache: {inserted} inserted, {updated} updated")
PY

    echo "=== [PRO 3/4] self-signed $TIER license + public key ==="
    # pro_keygen mints an ephemeral keypair, signs a tier=$TIER license (modules +
    # features derived from the canonical tier definitions), and writes
    # public_key.pem so THIS box (and only this box) trusts it. Run under the
    # server venv with the Pro+ repo on sys.path (it has the signer + cryptography);
    # no separate Pro+ venv needed.
    TIER="$TIER" PRO_PLUS_DIR="$PRO" OUT_DIR="$LICDIR" "$SVPY" /vagrant/pro_keygen.py
    LIC="$(cat "$LICDIR/license.jwt")"
    LIC="$LIC" "$SVPY" - <<'PY' || echo "  (yaml license inject failed)"
import os, yaml
cfg = yaml.safe_load(open('/etc/sysmanage.yaml'))
# phone_home_url="" is the crux: without it, config.config defaults it to the real
# license.sysmanage.org, and get_public_key_pem() fetches the PRODUCTION public key
# (overwriting our self-signed public_key.pem) so this demo license fails signature
# verification and the server drops to Community. Blanking it makes fetch fail fast,
# falling back to our cached self-signed key — and disables the download/phone-home
# background tasks (they all guard on a truthy phone_home_url). Validation is purely
# local, so the engines activate offline.
cfg['license'] = {
    'key': os.environ['LIC'],
    'modules_path': '/var/lib/sysmanage/modules',
    'phone_home_url': '',
}
yaml.safe_dump(cfg, open('/etc/sysmanage.yaml', 'w'), sort_keys=False)
PY

    echo "=== [PRO 4/4] restart + verify loaded engines (box stays $TIER-licensed) ==="
    cd /opt/sysmanage && make stop >/dev/null 2>&1 || true
    nohup make start > /var/log/sysmanage-start.log 2>&1 &
    sleep 35
    echo "  server-info:"
    curl -fsS http://localhost:8080/api/v1/server-info 2>/dev/null \
        | "$SVPY" -c "import sys,json; d=json.load(sys.stdin); print('    tier:', d.get('license_tier'), '| loaded_engines:', d.get('loaded_engines'))" \
        2>/dev/null || echo "    (server-info unavailable — check /var/log/sysmanage-start.log)"
fi

echo
echo "=== provision complete ==="
echo "Backend:  http://localhost:8080   Web UI: http://localhost:3000"
echo "Next (from the host): make screenshots-seed && make screenshots-capture"
