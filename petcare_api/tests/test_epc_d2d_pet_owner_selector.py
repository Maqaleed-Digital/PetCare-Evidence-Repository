"""MVC-EPC-D-001 D2d — Sponsor ruling R13.5 (R11-equivalent defect search): POST /api/pets let a platform admin name ANY
owner_id. It is now a selector validated against the session tenant (the rule POST /api/deliveries already applies); an
owner's own request never takes an owner_id from the body."""
import os
import sys
import uuid

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

pytestmark = pytest.mark.served_app


def _client(user_id, tenant, role):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@d2d-sel.test", "pw", role, tenant_id=tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@d2d-sel.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _world():
    tag = uuid.uuid4().hex[:6]
    t, other = f"t-d2d-sel-{tag}", f"t-d2d-sel-other-{tag}"
    ids = {k: f"u-d2d-sel-{k}-{tag}" for k in ("admin", "owner", "vet", "foreign")}
    return (ids, _client(ids["admin"], t, "platform_admin"), _client(ids["owner"], t, "owner"),
            _client(ids["vet"], t, "veterinarian"), _client(ids["foreign"], other, "owner"))


def test_an_admin_may_create_a_pet_only_for_an_owner_of_their_tenant():
    ids, admin, _owner, _vet, _foreign = _world()
    ok = admin.post("/api/pets", json={"name": "Luna", "species": "cat", "owner_id": ids["owner"]})
    assert ok.status_code == 200, ok.text
    assert ok.json()["owner_id"] == ids["owner"]
    for bad in (ids["foreign"], ids["vet"], f"u-does-not-exist-{uuid.uuid4().hex[:6]}"):
        r = admin.post("/api/pets", json={"name": "Max", "species": "dog", "owner_id": bad})
        assert r.status_code == 400, (bad, r.text)
        assert r.json()["detail"] == "owner_id is not an owner of this tenant"


def test_an_owner_never_takes_the_owner_from_the_body():
    ids, _admin, owner, _vet, _foreign = _world()
    r = owner.post("/api/pets", json={"name": "Bella", "species": "cat", "owner_id": ids["foreign"]})
    assert r.status_code == 200, r.text
    assert r.json()["owner_id"] == ids["owner"]
