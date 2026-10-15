"""MVC-EPC-D-001 D2m — J-O8 cash on delivery (R19.5 item 3): an owner shops by the registered product name. The orderable
catalogue and each order line carry `name` (additive); POM products stay unlisted and unorderable (FR-04/FR-20 unchanged)."""
import os
import sys
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
from inventory import REGISTRATION_SOURCE, ProductRegistration  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

pytestmark = pytest.mark.served_app


def _client(user_id, tenant, role):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@jo8.test", "pw", role, tenant_id=tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@jo8.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def test_the_catalogue_and_order_lines_carry_the_registered_name_and_pom_stays_out():
    tag = uuid.uuid4().hex[:6]
    t = f"t-d2m-{tag}"
    admin, owner = _client(f"u-jo8-adm-{tag}", t, "partner_clinic_admin"), _client(f"u-jo8-own-{tag}", t, "owner")
    gen, pom = f"gen-{tag}", f"pom-{tag}"
    for pid, name, cls in ((gen, "شامبو للكلاب", "GENERAL"), (pom, "Amoxicillin 250", "POM")):
        api.INVENTORY_REPO.register_product(ProductRegistration(product_id=pid, name=name, supply_class=cls,
                                                                source=REGISTRATION_SOURCE, registered_at=datetime.now(timezone.utc)))
        assert admin.post("/api/catalog/prices", json={"product_id": pid, "unit_price_halalas": 900}).status_code == 200
    listed = {x["product_id"]: x for x in owner.get("/api/catalog/prices").json()}
    assert listed[gen]["name"] == "شامبو للكلاب" and pom not in listed
    o = owner.post("/api/orders", json={"payment_method": "COD", "lines": [{"product_id": gen, "quantity": 3}]})
    assert o.status_code == 200, o.text
    assert o.json()["lines"] == [{"product_id": gen, "name": "شامبو للكلاب", "quantity": 3, "unit_price_halalas": 900}]
    assert [l["name"] for x in owner.get("/api/orders").json() for l in x["lines"]] == ["شامبو للكلاب"]
    r = owner.post("/api/orders", json={"payment_method": "COD", "lines": [{"product_id": pom, "quantity": 1}]})
    assert r.status_code == 409 and r.json()["detail"]["error"] == "PRESCRIPTION_PRODUCT_NOT_ORDERABLE"


def test_an_unregistered_product_has_no_name():
    assert api.INVENTORY_REPO.name_of(f"never-{uuid.uuid4().hex}") is None
