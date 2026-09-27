"""MVC-EPC-D-001 Lane D, D1 — the seven SQ-3 operations that were not served, through the SERVED app with step-up ON.

#4 sign medical record · #5 change role (always-fresh) · #11 personal-data export · #12 payout details (always-fresh) ·
#13 bank details (always-fresh) · #14 issue credentials · #15 issue API keys. The step-up challenge on each is also
proven for every role by test_nfr08_sq3.py::test_every_served_sensitive_operation_challenges_every_role.
"""
import hashlib
import logging
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
import sq3_ops  # noqa: E402
from routers import auth  # noqa: E402
from test_nfr08_sq3 import _client, _enrol, _step_up, clock  # noqa: E402,F401

pytestmark = [pytest.mark.served_app, pytest.mark.mfa_enforced]
IBAN = "SA0380000000608010167519"                       # the published ISO 13616 example for Saudi Arabia


def _ready(user_id, role, tenant, clock):
    c = _client(user_id, role, tenant)
    return c, _enrol(c, clock)[0]


def test_4_a_veterinarian_signs_a_medical_record_once_and_it_is_then_immutable(clock):
    t = "t-d1-sign"
    vet, vs = _ready("u-d1-vet", "veterinarian", t, clock)
    owner, os_ = _ready("u-d1-owner", "owner", t, clock)
    pet = owner.post("/api/pets", json={"name": "Luna", "species": "cat"}).json()
    rec = vet.post(f"/api/pets/{pet['pet_id']}/medical-records",
                   json={"record_type": "CLINICAL_RECORD", "title": "Exam", "detail": "healthy"}).json()
    sign = f"/api/pets/{pet['pet_id']}/medical-records/{rec['record_id']}/sign"
    assert vet.post(sign).json()["detail"]["error"] == "MFA_STEP_UP_REQUIRED"
    _step_up(vet, vs, clock)
    signed = vet.post(sign).json()
    assert signed["signed_by_actor_id"] == "u-d1-vet" and signed["signed_at"] and len(signed["content_sha256"]) == 64
    r = vet.post(sign)
    assert r.status_code == 409 and r.json()["detail"]["error"] == "MEDICAL_RECORD_ALREADY_SIGNED"
    _step_up(owner, os_, clock)
    assert owner.post(sign).status_code == 403                                   # owners never sign
    other, ots = _ready("u-d1-vet-x", "veterinarian", "t-d1-sign-x", clock)
    _step_up(other, ots, clock)
    assert other.post(sign).status_code == 404                                   # another tenant's vet


def test_5_role_change_is_always_fresh_bounded_by_the_admin_and_revokes_the_subject_sessions(clock):
    t = "t-d1-role"
    admin, s = _ready("u-d1-admin", "partner_clinic_admin", t, clock)
    subject = _client("u-d1-subj", "veterinarian", t)
    auth.seed_user("u-d1-subj2", "u-d1-subj2@sq3.test", "pw", "owner", tenant_id=t)
    _client("u-d1-elsewhere", "owner", "t-d1-role-other")
    url = "/api/admin/identities/u-d1-subj/role"
    _step_up(admin, s, clock)
    r = admin.post(url, json={"role": "owner"})
    assert r.status_code == 200 and r.json()["changed"] is True and r.json()["sessions_revoked"] >= 1
    assert subject.get("/api/auth/me").status_code == 401                          # the old role's session is gone
    assert auth.IDENTITY_REPO.get_by_user_id("u-d1-subj").role == "owner"
    r = admin.post("/api/admin/identities/u-d1-subj2/role", json={"role": "veterinarian"})
    assert r.status_code == 403 and r.json()["detail"]["always_fresh"] is True     # a second change needs a new step-up
    _step_up(admin, s, clock)
    assert admin.post(url, json={"role": "platform_admin"}).json()["detail"]["error"] == "ROLE_NOT_ASSIGNABLE"
    _step_up(admin, s, clock)
    assert admin.post("/api/admin/identities/u-d1-admin/role",
                      json={"role": "owner"}).json()["detail"]["error"] == "ROLE_SELF_CHANGE_REFUSED"
    _step_up(admin, s, clock)
    assert admin.post("/api/admin/identities/u-d1-elsewhere/role", json={"role": "owner"}).status_code == 404
    _step_up(admin, s, clock)
    events = [e for e in admin.get("/audit/events/tenant", params={"limit": 5000}).json()["events"]
              if e["event_name"] == "identity.role.changed"]
    assert events and events[-1]["reason_code"] == "veterinarian->owner" and events[-1]["actor_id"] == "u-d1-admin"


def test_11_an_owner_downloads_their_own_personal_data_and_no_secret(clock):
    owner, s = _ready("u-d1-exp", "owner", "t-d1-exp", clock)
    owner.post("/api/pets", json={"name": "Milo", "species": "dog"})
    assert owner.get("/api/me/export").json()["detail"]["error"] == "MFA_STEP_UP_REQUIRED"
    _step_up(owner, s, clock)
    r = owner.get("/api/me/export")
    assert r.status_code == 200 and "attachment" in r.headers["content-disposition"]
    body = r.json()
    assert body["identity"]["user_id"] == "u-d1-exp" and [p["name"] for p in body["pets"]] == ["Milo"]
    text = r.text.lower()
    for forbidden in ("password", "scrypt", "otpauth", "recovery", "ciphertext", "session"):
        assert forbidden not in text, forbidden


def test_12_13_payout_and_bank_details_are_always_fresh_and_the_iban_is_never_returned_or_logged(clock, caplog):
    admin, s = _ready("u-d1-fin", "partner_clinic_admin", "t-d1-fin", clock)
    _step_up(admin, s, clock)
    p = admin.put("/api/admin/tenant/payout-details", json={"payout_schedule": "MONTHLY", "minimum_payout_halalas": 10000})
    assert p.status_code == 200 and p.json()["payout_schedule"] == "MONTHLY"
    again = admin.put("/api/admin/tenant/payout-details", json={"payout_schedule": "WEEKLY"})
    assert again.status_code == 403 and again.json()["detail"]["always_fresh"] is True   # #12 itself is always-fresh
    _step_up(admin, s, clock)
    assert admin.get("/audit/events/tenant").status_code == 200                    # a NORMAL op uses this step-up …
    r = admin.put("/api/admin/tenant/bank-details", json={"bank_name": "Bank", "account_holder": "Clinic", "iban": IBAN})
    assert r.status_code == 403 and r.json()["detail"]["always_fresh"] is True     # … so it is not new for #13
    with caplog.at_level(logging.DEBUG):
        _step_up(admin, s, clock)
        assert admin.put("/api/admin/tenant/bank-details",
                         json={"bank_name": "Bank", "account_holder": "Clinic", "iban": "SA0380000000608010167518"}
                         ).json()["detail"]["error"] == "BANK_DETAILS_INVALID"     # mod-97 fails
        _step_up(admin, s, clock)
        b = admin.put("/api/admin/tenant/bank-details",
                      json={"bank_name": "Bank", "account_holder": "Clinic", "iban": "sa03 8000 0000 6080 1016 7519"})
    assert b.status_code == 200 and b.json()["iban_masked"].endswith("7519") and IBAN not in b.text
    assert IBAN not in admin.get("/api/admin/tenant/bank-details").text and IBAN not in caplog.text
    stored = api.SQ3_OPS.bank(tenant_id="t-d1-fin")
    assert IBAN.encode() not in stored.iban_ciphertext and stored.iban_last4 == "7519"
    owner, os_ = _ready("u-d1-fin-owner", "owner", "t-d1-fin", clock)
    _step_up(owner, os_, clock)
    assert owner.put("/api/admin/tenant/payout-details", json={"payout_schedule": "WEEKLY"}).status_code == 403


def test_14_an_issued_credential_is_shown_once_stored_one_way_redeemed_once_and_never_logged(clock, caplog):
    admin, s = _ready("u-d1-cred", "partner_clinic_admin", "t-d1-cred", clock)
    _step_up(admin, s, clock)
    assert admin.post("/api/admin/credentials", json={"role": "platform_admin"}).json()["detail"]["error"] == \
        "CREDENTIAL_REQUEST_INVALID"                                              # a clinic admin cannot mint platform admins
    with caplog.at_level(logging.DEBUG):
        _step_up(admin, s, clock)
        issued = admin.post("/api/admin/credentials", json={"role": "owner", "expires_in_days": 3}).json()
        raw = issued["credential"]
        assert issued["shown_once"] is True and auth.INVITE_REPO.get(raw) is None
        assert auth.INVITE_REPO.get(sq3_ops.credential_key(raw)).tenant_id == "t-d1-cred"
        reg = {"email": "invited@d1.test", "password": "Pw-long-enough-1", "invite_code": raw, "role": "owner", "name": "x"}
        assert TestClient(api.app).post("/api/auth/register", json=reg).status_code == 201
        again = TestClient(api.app).post("/api/auth/register", json={**reg, "email": "second@d1.test"})
        assert again.status_code == 400 and again.json()["detail"]["error"] == "INVALID_INVITE"
    assert raw not in caplog.text and raw.replace("-", "") not in caplog.text


def test_15_an_api_key_is_shown_once_stored_as_sha256_listed_by_prefix_and_revocable(clock, caplog):
    admin, s = _ready("u-d1-keys", "platform_admin", "t-d1-keys", clock)
    with caplog.at_level(logging.DEBUG):
        _step_up(admin, s, clock)
        issued = admin.post("/api/admin/api-keys", json={"name": "integration"}).json()
    key = issued["api_key"]
    assert key.startswith("pck_") and issued["shown_once"] is True and key not in caplog.text
    listed = admin.get("/api/admin/api-keys").json()
    assert [k["prefix"] for k in listed] == [key[:12]] and key not in str(listed)
    stored = api.SQ3_OPS.api_keys(tenant_id="t-d1-keys")[0]
    assert stored.key_sha256 == hashlib.sha256(key.encode()).hexdigest() and key not in repr(stored)
    assert admin.post(f"/api/admin/api-keys/{stored.key_id}/revoke").json()["revoked"] is True
    assert admin.post(f"/api/admin/api-keys/{stored.key_id}/revoke").status_code == 404
    clinic, cs = _ready("u-d1-keys-ca", "partner_clinic_admin", "t-d1-keys", clock)
    _step_up(clinic, cs, clock)
    assert clinic.post("/api/admin/api-keys", json={"name": "x"}).status_code == 403   # platform admin only
