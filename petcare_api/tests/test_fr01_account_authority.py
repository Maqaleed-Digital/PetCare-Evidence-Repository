"""FR-01 multi-role accounts — U20 (MVC-BUILD-RUNNER-001), through the SERVED app.

AC-FR-01-03 (built here in part; NOT registered while SPONSOR_QUEUE SQ-1 is open): tenant authority is server-held
(the session record + the identity's current membership, never the token); a moved or ended membership fails every
older session closed; ending a membership leaves history attributable; session-bearing account actions (sign-in,
sign-out) are in the audit chain. Pre-session events (registration, failed sign-in) are SQ-1's question.
AC-FR-01-04 (dependency COUNSEL:L-2): no general-purpose pharmacy role exists and no role holds pharmacy authority
not scoped to a supply class — the class-scoped authority itself awaits counsel and is not evidenced.
"""
import dataclasses
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
import roles  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant, grant_practitioner_authority, stock_origin  # noqa: E402

pytestmark = pytest.mark.served_app
T_A, T_B = "t-fr01u20-alpha", "t-fr01u20-beta"


def _client(user_id, tenant, role):
    for t in (T_A, T_B):
        ensure_tenant(t)
    auth.seed_user(user_id, f"{user_id}@u20.test", "pw", role, tenant_id=tenant)
    if role == "veterinarian":
        grant_practitioner_authority(user_id, tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@u20.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    c.session_token = r.cookies["petcare_session"]
    return c


def _move(user_id, tenant):
    """Membership change is a governed durable act (PG route proven in test_tenant_membership_postgres.py)."""
    ident = auth.IDENTITY_REPO.get_by_user_id(user_id)
    auth.IDENTITY_REPO.upsert(dataclasses.replace(ident, tenant_id=tenant))


def _events(c, name=None):
    return [e for e in c.get("/audit/events/tenant", params={"limit": 5000}).json()["events"]
            if name is None or e["event_name"] == name]


# --------------------------------------------------------------------------- AC-FR-01-03 (partial; not registered)
def test_tenant_authority_is_server_held_and_a_moved_membership_fails_closed():
    owner = _client("u-u20-owner", T_A, "owner")
    assert owner.get("/api/pets").status_code == 200
    old = owner.session_token
    payload = auth._serializer().loads(old)
    forged = auth._serializer().dumps({**payload, "tenant_id": T_B})       # a token claiming another tenant
    probe = TestClient(api.app)
    probe.cookies.set("petcare_session", forged)
    assert probe.get("/api/pets").status_code == 401
    _move("u-u20-owner", T_B)
    r = owner.get("/api/pets")
    assert r.status_code == 401 and r.json()["detail"]["error"] == "SESSION_TENANT_STALE"
    _move("u-u20-owner", None)
    assert owner.get("/api/pets").status_code == 401


def test_sign_in_and_sign_out_are_chained_and_sign_out_ends_the_session():
    vet = _client("u-u20-vet", T_A, "veterinarian")
    sid = auth._serializer().loads(vet.session_token)["sid"]
    admin = _client("u-u20-admin", T_A, "partner_clinic_admin")
    signed_in = [e for e in _events(admin, "account.signed_in") if e["resource_id"] == sid]
    assert len(signed_in) == 1 and signed_in[0]["actor_id"] == "u-u20-vet"
    cookie = vet.session_token
    assert vet.post("/api/auth/sign-out").status_code == 200
    signed_out = [e for e in _events(admin, "account.signed_out") if e["resource_id"] == sid]
    assert len(signed_out) == 1 and signed_out[0]["actor_id"] == "u-u20-vet" and signed_out[0]["tenant_id"] == T_A
    replay = TestClient(api.app)
    replay.cookies.set("petcare_session", cookie)
    assert replay.get("/api/pets").status_code == 401                        # the copied cookie is dead


def test_ending_a_membership_keeps_history_attributable():
    owner = _client("u-u20-owner2", T_A, "owner")
    admin = _client("u-u20-admin2", T_A, "partner_clinic_admin")
    pet = owner.post("/api/pets", json={"name": "Luna", "species": "cat"}).json()
    _move("u-u20-owner2", None)                                             # the membership ends
    created = [e for e in _events(admin, "pet.profile.created") if e["resource_id"] == pet["pet_id"]]
    assert created and created[0]["actor_id"] == "u-u20-owner2"
    ident = auth.IDENTITY_REPO.get_by_user_id("u-u20-owner2")
    assert ident is not None and ident.user_id == "u-u20-owner2"            # still resolvable: attributable
    assert api.PET_REPO.get(pet["pet_id"], tenant_id=T_A).created_by_actor_id == "u-u20-owner2"


# --------------------------------------------------------------------------- AC-FR-01-04 (internal part)
def test_no_general_purpose_pharmacy_role_exists_and_no_role_dispenses_unscoped():
    assert not [r for r in roles.ALLOWED_ROLES if "pharm" in r.lower()]
    vet = _client("u-u20-vet4", T_A, "veterinarian")
    rx = vet.post("/api/prescriptions", json={"pet_id": "p", "session_id": "s", "medication_name": "m", "dosage": "d",
                                              "instructions": "i"}).json()["prescription_id"]
    assert vet.post(f"/api/prescriptions/{rx}/verify").status_code == 200
    for role in sorted(roles.ALLOWED_ROLES - {"veterinarian"}):
        c = _client(f"u-u20-{role}", T_A, role)
        r = c.post(f"/api/prescriptions/{rx}/dispense", json=stock_origin(T_A),
                   headers={"X-Petcare-Role": "pharmacist", "X-Professional-Class": "PHARMACIST"})
        assert r.status_code == 403, (role, r.status_code)
    denied = {e["actor_id"] for e in _events(vet, "prescription.dispense_denied") if e["resource_id"] == rx}
    assert denied >= {f"u-u20-{r}" for r in roles.ALLOWED_ROLES - {"veterinarian"}}
    assert vet.get(f"/api/prescriptions/{rx}").json()["status"] == "VET_VERIFIED"
