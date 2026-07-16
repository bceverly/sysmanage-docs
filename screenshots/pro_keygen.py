#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Self-sign a demo license (any tier) for the throwaway screenshot VM.

We don't (and can't) use the production signing key. Instead we mint an EPHEMERAL
ECDSA P-521 keypair, inject it into the Pro+ license signer, and sign a license
for ``TIER`` (default 'professional'). The modules + features granted are DERIVED
from the canonical signing-side tier definitions
(backend.licensing.features.get_modules_for_tier / get_features_for_tier) so the
demo license always matches what a real license of that tier would grant — no
hand-maintained lists to drift. The matching public key is written so the VM's
server trusts it: it reads its verification key from
/var/lib/sysmanage/license/public_key.pem (cache-file-first), so dropping our
public key there makes the VM — and ONLY the VM — trust this demo license.

Run with the Pro+ repo on sys.path (it has the signer + features + cryptography).
Outputs (both gitignored, demo-only):
    license.jwt      the signed JWT (-> sysmanage.yaml license.key)
    public_key.pem   our public key (-> VM /var/lib/sysmanage/license/)

Usage:
    TIER=enterprise PRO_PLUS_DIR=/path/to/sysmanage-professional-plus OUT_DIR=. python3 pro_keygen.py
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone

PRO_PLUS_DIR = os.environ.get("PRO_PLUS_DIR", "/srv/src/sysmanage-professional-plus")
OUT_DIR = os.environ.get("OUT_DIR", os.path.dirname(__file__) or ".")
TIER = os.environ.get("TIER", "professional")


def main() -> int:
    sys.path.insert(0, PRO_PLUS_DIR)
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec

    # Ephemeral keypair, injected straight into the signer singleton (it returns
    # this without touching the encrypted key file / passphrase / config).
    priv = ec.generate_private_key(ec.SECP521R1())
    from backend.licensing import key_manager as km_mod  # noqa: PLC0415
    km_mod.key_manager._private_key = priv  # pylint: disable=protected-access
    km_mod.key_manager._public_key = priv.public_key()

    # Canonical tier -> modules/features (the same source the real signer uses),
    # so a 'professional' license grants exactly the Pro engines and an
    # 'enterprise' license grants the full Enterprise engine set — never
    # multitenancy (that's the multitenant_saas tier only).
    from backend.licensing.features import (  # noqa: PLC0415
        get_features_for_tier,
        get_modules_for_tier,
    )
    from backend.licensing.generator import generate_license_token  # noqa: PLC0415

    modules = get_modules_for_tier(TIER)
    features = get_features_for_tier(TIER)
    if not modules:
        print(f"ERROR: unknown/empty tier '{TIER}' — no modules to grant")
        return 1

    now = datetime.now(timezone.utc)
    license_key, _nonce = generate_license_token(
        license_id=f"SCREENSHOT-{TIER.upper()}",
        customer_id="DOCS",
        organization="SysManage Documentation",
        tier=TIER,
        features=features,
        modules=modules,
        parent_hosts=1000,
        child_hosts=10000,
        issued_at=now,
        expires_at=now + timedelta(days=3650),
        grace_period=3650,
        offline_days=3650,  # never needs to phone home
    )

    pub_pem = priv.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    with open(os.path.join(OUT_DIR, "license.jwt"), "w", encoding="utf-8") as fh:
        fh.write(license_key)
    with open(os.path.join(OUT_DIR, "public_key.pem"), "wb") as fh:
        fh.write(pub_pem)
    print(f"wrote license.jwt ({len(license_key)} chars) + public_key.pem")
    print(f"  tier={TIER}  modules={len(modules)}  features={len(features)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
