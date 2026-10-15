"""MVC-EPC-D-001 D2m — PostgreSQL: the inventory store answers the registered product name an owner shops by (J-O8)."""
import os
import sys
from datetime import datetime, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
from inventory import REGISTRATION_SOURCE, ProductRegistration  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402

ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}


def test_the_registered_name_survives_a_second_instance(clean_postgres):
    p = build_persistence(ENV, connection_url=clean_postgres)
    p.inventory.register_product(ProductRegistration(product_id="pg-gen", name="شامبو للكلاب", supply_class="GENERAL",
                                                     source=REGISTRATION_SOURCE, registered_at=datetime(2031, 3, 1, tzinfo=timezone.utc)))
    again = build_persistence(ENV, connection_url=clean_postgres)
    assert again.inventory.name_of("pg-gen") == "شامبو للكلاب" and again.inventory.name_of("pg-none") is None
    p.pool.close(); again.pool.close()
