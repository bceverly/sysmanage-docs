#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Set the server_configuration singleton's air-gap + federation roles (in-VM).

The air-gap (collections/repositories) and federation (Sites) UIs only render
real content when the server's role matches — the route mounting happens at
backend startup, so the server must be restarted after changing a role. Used by
`make screenshots-ent-roles` to flip roles between capture passes.

Env (only the ones provided are changed):
    AIR_GAP_ROLE    standard | collector | repository
    FEDERATION_ROLE none | coordinator | site
"""
import os

from sqlalchemy.orm import sessionmaker

from backend.persistence import db
from backend.persistence.models import ServerConfiguration


def main():
    session = sessionmaker(bind=db.get_engine())()
    try:
        cfg = session.query(ServerConfiguration).first()
        if cfg is None:
            cfg = ServerConfiguration()  # fixed singleton id via the model default
            session.add(cfg)
        ag = os.environ.get("AIR_GAP_ROLE")
        fr = os.environ.get("FEDERATION_ROLE")
        if ag:
            cfg.air_gap_role = ag
        if fr:
            cfg.federation_role = fr
        session.commit()
        print(f"  server roles: air_gap_role={cfg.air_gap_role} "
              f"federation_role={cfg.federation_role}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
