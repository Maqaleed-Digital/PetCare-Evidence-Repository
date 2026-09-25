"""FR-05 veterinarian licence registration and verification — ratified AC-FR-05-01/02 through the
SERVED app (MVC-BUILD-RUNNER-001 U10).

AC-FR-05-03/04 depend on EXTERNAL:VET_LICENSING_AUTHORITY. The lookup port's fail-closed contract
is exercised here with a double of OUR reading of the interface; that is not the authority's
contract and is not registered as evidence for either criterion.
"""
import dataclasses
import os
import sys
import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import licences  # noqa: E402
import main as api  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

pytestmark = pytest.mark.served_app
T_A, T_B = "t-fr05-alpha", "t-fr05-beta"
PW = "Pw-long-enough-1"
RX = {"pet_id": "p1", "session_id": "s1", "medication_name": "Amoxicillin", "dosage": "50mg", "instructions": "bid"}
FUTURE = (date.today() + timedelta(days=365)).isoformat()


def _signin(email):
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": email, "password": PW})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _seeded(user_id, tenant, role):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@fr05.test", PW, role, tenant_id=tenant)
    return _signin(f"{user_id}@fr05.test")


def _register_vet(tenant, *, licence=True, expires_on=FUTURE, code=None):
    ensure_tenant(tenant)
    code = code or f"FR05-{uuid.uuid4().hex[:8]}"
    auth.seed_invite_code(code, "veterinarian")
    email = f"vet-{uuid.uuid4().hex[:8]}@fr05.test"
    body = {"email": email, "password": PW, "invite_code": code, "role": "veterinarian", "name": "Dr Test"}
    if licence:
        body["licence"] = {"licence_number": f"MEWA-{uuid.uuid4().hex[:6]}", "issuing_authority": "MEWA",
                           "expires_on": expires_on}
    return TestClient(api.app).post("/api/auth/register", json=body), email, code


def _assign(email, tenant):
    """Tenant assignment is a governed durable act (proven in test_tenant_membership_postgres.py); a fixture here."""
    ident = auth.IDENTITY_REPO.get_by_email(email)
    auth.IDENTITY_REPO.upsert(dataclasses.replace(ident, tenant_id=tenant))
    return ident.user_id


def _events(c, name):
    return [e for e in c.get("/audit/events/tenant", params={"limit": 5000}).json()["events"] if e["event_name"] == name]


def _licence_id(admin, user_id):
    return next(x["licence_id"] for x in admin.get("/api/admin/practitioners/licences").json() if x["actor_id"] == user_id)


# --------------------------------------------------------------------------- AC-FR-05-01
def test_a_veterinarian_cannot_register_without_licence_details():
    r, _e, code = _register_vet(T_A, licence=False)
    assert r.status_code == 400 and r.json()["detail"]["error"] == "LICENCE_DETAILS_REQUIRED"
    expired, _e2, code2 = _register_vet(T_A, expires_on=(date.today() - timedelta(days=1)).isoformat())
    assert expired.status_code == 400 and expired.json()["detail"]["error"] == "LICENCE_EXPIRED"
    # The refusal did not spend the invite: the same code registers once licence details are given.
    ok, email, _ = _register_vet(T_A, code=code)
    assert ok.status_code == 201, ok.text
    mine = _signin(email).get("/api/practitioners/me/licence").json()
    assert len(mine) == 1 and mine[0]["status"] == "SUBMITTED" and mine[0]["issuing_authority"] == "MEWA"


def test_an_unverified_vet_performs_no_clinical_act_until_the_licence_is_verified():
    admin = _seeded("u-fr05-admin", T_A, "platform_admin")
    owner = _seeded("u-fr05-owner", T_A, "owner")
    r, email, _ = _register_vet(T_A)
    assert r.status_code == 201
    vet_id = _assign(email, T_A)
    vet = _signin(email)
    pet = owner.post("/api/pets", json={"name": "Luna", "species": "cat"}).json()
    sess = vet.post("/api/consultations", json={"pet_id": pet["pet_id"], "owner_id": "u-fr05-owner",
                                                "veterinarian_id": vet_id, "tenant_id": T_A}).json()
    acts = {
        "issue prescription": lambda: vet.post("/api/prescriptions", json=RX),
        "clinical note": lambda: vet.post(f"/api/consultations/{sess['session_id']}/notes",
                                          json={"session_id": sess["session_id"], "pet_id": pet["pet_id"],
                                                "content": "exam", "tenant_id": T_A}),
        "medical record": lambda: vet.post(f"/api/pets/{pet['pet_id']}/medical-records",
                                           json={"record_type": "LAB_RESULT", "title": "CBC"}),
    }
    for name, act in acts.items():
        res = act()
        assert res.status_code == 403, (name, res.text)
        assert res.json()["detail"]["error"] == "PRACTITIONER_AUTHORITY_REQUIRED", name
    refused = [e for e in _events(admin, "practitioner.authority.refused") if e["actor_id"] == vet_id]
    assert len(refused) >= 3 and all(e["action_result"] == "denied" for e in refused)
    v = admin.post(f"/api/admin/practitioners/licences/{_licence_id(admin, vet_id)}/verify",
                   json={"method": "MANUAL_STAFF", "basis": "MEWA public register checked 2026-09-25"})
    assert v.status_code == 200, v.text
    for name, act in acts.items():
        assert act().status_code == 200, name
    audit = [e for e in _events(admin, "practitioner.licence.verified") if e["resource_id"] == v.json()["licence_id"]]
    assert len(audit) == 1 and audit[0]["actor_id"] == "u-fr05-admin" and audit[0]["reason_code"].startswith("MANUAL_STAFF")


# --------------------------------------------------------------------------- AC-FR-05-02
def test_a_verification_records_who_when_how_and_against_what_and_is_tenant_scoped():
    admin = _seeded("u-fr05-admin2", T_A, "platform_admin")
    admin_b = _seeded("u-fr05-admin2b", T_B, "platform_admin")
    _r, email, _ = _register_vet(T_A)
    vet_id = _assign(email, T_A)
    lid = _licence_id(admin, vet_id)
    assert lid not in [x["licence_id"] for x in admin_b.get("/api/admin/practitioners/licences").json()]
    assert admin_b.post(f"/api/admin/practitioners/licences/{lid}/verify",
                        json={"method": "MANUAL_STAFF", "basis": "x"}).status_code == 404
    assert admin.post(f"/api/admin/practitioners/licences/{lid}/verify",
                      json={"method": "MANUAL_STAFF", "basis": "  "}).status_code == 400
    before = datetime.now(timezone.utc)
    ok = admin.post(f"/api/admin/practitioners/licences/{lid}/verify",
                    json={"method": "MANUAL_STAFF", "basis": "MEWA register entry sighted"}).json()
    ver = ok["verification"]
    assert ok["status"] == "VERIFIED" and ver["verified_by_actor_id"] == "u-fr05-admin2"
    assert ver["method"] == "MANUAL_STAFF" and ver["basis"] == "MEWA register entry sighted"
    assert datetime.fromisoformat(ver["verified_at"]) >= before
    assert admin.post(f"/api/admin/practitioners/licences/{lid}/verify",
                      json={"method": "MANUAL_STAFF", "basis": "again"}).status_code == 409
    grant = next(g for g in _signin(email).get("/api/practitioners/me/authority").json()["grants"]
                 if g["grant_id"] == ver["grant_id"])
    assert grant["expires_at"].startswith((date.fromisoformat(FUTURE) + timedelta(days=1)).isoformat())


def test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act(monkeypatch):
    admin = _seeded("u-fr05-admin3", T_A, "platform_admin")
    today = date.today().isoformat()
    _r, email, _ = _register_vet(T_A, expires_on=today)  # valid through the end of today
    vet_id = _assign(email, T_A)
    admin.post(f"/api/admin/practitioners/licences/{_licence_id(admin, vet_id)}/verify",
               json={"method": "MANUAL_STAFF", "basis": "sighted"})
    vet = _signin(email)
    assert vet.post("/api/prescriptions", json=RX).status_code == 200

    real = datetime

    class _Later(real):
        @classmethod
        def now(cls, tz=None):
            return real.now(tz) + timedelta(days=2)

    monkeypatch.setattr(api, "datetime", _Later)  # the clock moves past the licence expiry
    r = vet.post("/api/prescriptions", json=RX)
    assert r.status_code == 403
    expiry = datetime.combine(date.today() + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)
    assert r.json()["detail"]["reason"] == f"expired at {expiry.isoformat()}"


# --------------------------------------------------------------------------- AC-FR-05-03 (port contract, not evidence)
def test_the_licensing_lookup_port_fails_closed(monkeypatch):
    admin = _seeded("u-fr05-admin4", T_A, "platform_admin")
    ids = {}
    for k in ("unconfigured", "valid", "not_found", "lapsed", "junk"):
        _r, email, _ = _register_vet(T_A)
        ids[k] = _licence_id(admin, _assign(email, T_A))
    r = admin.post(f"/api/admin/practitioners/licences/{ids['unconfigured']}/verify", json={"method": "AUTHORITY_LOOKUP"})
    assert r.status_code == 409 and r.json()["detail"]["lookup"] == "UNAVAILABLE"

    class _Double:
        def lookup(self, *, licence_number, issuing_authority):
            return answers[licence_number]

    answers = {}
    for k, lid in ids.items():
        num = api.LICENCE_REPO.get(lid).licence_number
        answers[num] = {"valid": licences.LookupResult("VALID"), "not_found": licences.LookupResult("NOT_FOUND"),
                        "lapsed": licences.LookupResult("LAPSED"), "junk": "yes",
                        "unconfigured": licences.LookupResult("UNAVAILABLE")}[k]
    monkeypatch.setattr(api, "LICENSING_PORT", _Double())
    got = {k: admin.post(f"/api/admin/practitioners/licences/{lid}/verify", json={"method": "AUTHORITY_LOOKUP"}).status_code
           for k, lid in ids.items() if k != "unconfigured"}
    assert got == {"valid": 200, "not_found": 409, "lapsed": 409, "junk": 409}
