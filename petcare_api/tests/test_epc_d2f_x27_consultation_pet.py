"""MVC-EPC-D-001 D2f — X-27 (Sponsor rulings R14.1, R16.5): a consultation's pet must belong to the selected owner in the
SESSION tenant. A client-supplied pet_id is only a selector; a client-supplied owner/tenant cannot widen the session."""
import os
import sys
import uuid

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant, grant_practitioner_authority  # noqa: E402

pytestmark = pytest.mark.served_app


def _client(user_id, tenant, role):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@d2f-x27.test", "pw", role, full_name=user_id, tenant_id=tenant)
    if role == "veterinarian":
        grant_practitioner_authority(user_id, tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@d2f-x27.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


@pytest.fixture()
def w():
    tag = uuid.uuid4().hex[:6]
    t, other = f"t-d2f-x27-{tag}", f"t-d2f-x27-other-{tag}"
    ids = {k: f"u-x27-{k}-{tag}" for k in ("owner", "owner2", "vet", "foreign_owner", "foreign_vet")}
    w = {"ids": ids, "t": t, "other": other,
         "owner": _client(ids["owner"], t, "owner"), "owner2": _client(ids["owner2"], t, "owner"),
         "vet": _client(ids["vet"], t, "veterinarian"),
         "foreign_owner": _client(ids["foreign_owner"], other, "owner"),
         "foreign_vet": _client(ids["foreign_vet"], other, "veterinarian")}
    for who in ("owner", "owner2", "foreign_owner"):
        w[f"pet_{who}"] = w[who].post("/api/pets", json={"name": "Luna", "species": "cat"}).json()["pet_id"]
    return w


def _start(w, pet, owner="owner", vet="vet", client="vet", **extra):
    return w[client].post("/api/consultations", json={"pet_id": pet, "owner_id": w["ids"][owner],
                                                      "veterinarian_id": w["ids"][vet], **extra})


def _refusals(w):
    ev = w["vet"].get("/audit/events/tenant", params={"limit": 5000}).json()["events"]
    return [e for e in ev if e["event_name"] == "consultation.session.refused"]


def test_a_consultation_for_the_selected_owners_own_pet_starts(w):
    r = _start(w, w["pet_owner"])
    assert r.status_code == 200, r.text
    assert (r.json()["pet_id"], r.json()["owner_id"], r.json()["tenant_id"]) == (w["pet_owner"], w["ids"]["owner"], w["t"])


def test_another_owners_pet_is_refused(w):
    r = _start(w, w["pet_owner2"])                                     # owner2's pet, consultation for owner
    assert r.status_code == 400 and r.json()["detail"]["error"] == "PET_NOT_OF_OWNER"
    assert [e["reason_code"] for e in _refusals(w)] == ["PET_NOT_OF_OWNER"]


def test_another_tenants_pet_is_refused(w):
    r = _start(w, w["pet_foreign_owner"])
    assert r.status_code == 400 and r.json()["detail"]["error"] == "PET_NOT_OF_OWNER"


def test_a_nonexistent_pet_is_refused(w):
    r = _start(w, "pet-that-does-not-exist")
    assert r.status_code == 400 and r.json()["detail"]["error"] == "PET_NOT_OF_OWNER"
    assert _start(w, "p1").status_code == 400                          # the old placeholder no longer starts one


def test_client_supplied_owner_and_tenant_cannot_override_the_session(w):
    # Naming the pet's real owner from another tenant does not widen the session tenant: that owner is not a participant
    # of this tenant, and the pet is not found in it.
    assert _start(w, w["pet_foreign_owner"], owner="foreign_owner").status_code == 400
    # A body tenant that disagrees with the session is refused outright, never honoured.
    assert _start(w, w["pet_foreign_owner"], owner="foreign_owner", tenant_id=w["other"]).status_code == 403
    # The other tenant's veterinarian, with the right owner and pet of THIS tenant, cannot start one either.
    assert _start(w, w["pet_owner"], vet="vet", client="foreign_vet").status_code == 400
    assert _start(w, w["pet_owner"]).json()["tenant_id"] == w["t"]


def test_the_pet_is_checked_against_the_selected_owner_not_only_the_tenant(w):
    # owner2's pet with owner2 selected starts; the same pet with owner selected does not.
    assert _start(w, w["pet_owner2"], owner="owner2").status_code == 200
    assert _start(w, w["pet_owner2"], owner="owner").status_code == 400
