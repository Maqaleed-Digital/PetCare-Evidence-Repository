"""MVC-EPC-D-001 D2g — X-22 clinical-act lapse (Sponsor ruling R17.2): a veterinary licence valid through expiry day D
authorises clinical acts until 23:59 Asia/Riyadh on D and is refused from 00:00 Asia/Riyadh on D+1 — consistently with
registration and repository validation (D2f, R16.3 Option B). The served clock (`main.datetime`) is pinned per case, so
the result is the same under any host TZ. 00:00 and 02:59 Riyadh on D+1 are the discriminating cells: the old UTC-midnight
lapse still admitted acts there.
"""
import dataclasses
import os
import sys
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

pytestmark = pytest.mark.served_app
T = "t-d2g-x22-lapse"
PW = "Pw-long-enough-1"
RX = {"pet_id": "p1", "session_id": "s1", "medication_name": "Amoxicillin", "dosage": "50mg", "instructions": "bid"}
EXPIRES_ON = "2031-03-10"                                          # day D
BEFORE = datetime(2031, 3, 1, 9, 0, tzinfo=timezone.utc)           # registration and verification
CELLS = {                                                          # Riyadh wall clock -> allowed?
    "D-2359": (datetime(2031, 3, 10, 20, 59, tzinfo=timezone.utc), True),
    "D+1-0000": (datetime(2031, 3, 10, 21, 0, tzinfo=timezone.utc), False),
    "D+1-0259": (datetime(2031, 3, 10, 23, 59, tzinfo=timezone.utc), False),
    "D+1-0300": (datetime(2031, 3, 11, 0, 0, tzinfo=timezone.utc), False),
}


def _pin(monkeypatch, module, instant):
    real = datetime

    class _Pinned(real):
        @classmethod
        def now(cls, tz=None):
            return instant.astimezone(tz) if tz is not None else instant.astimezone().replace(tzinfo=None)

    monkeypatch.setattr(module, "datetime", _Pinned)


def _signin(email):
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": email, "password": PW})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _verified_vet(monkeypatch):
    ensure_tenant(T)
    _pin(monkeypatch, auth, BEFORE)
    _pin(monkeypatch, api, BEFORE)
    admin_id = f"u-d2g-admin-{uuid.uuid4().hex[:6]}"
    auth.seed_user(admin_id, f"{admin_id}@d2g.test", PW, "platform_admin", tenant_id=T)
    code = f"D2G-{uuid.uuid4().hex[:8]}"
    auth.seed_invite_code(code, "veterinarian")
    email = f"vet-{uuid.uuid4().hex[:8]}@d2g.test"
    r = TestClient(api.app).post("/api/auth/register", json={
        "email": email, "password": PW, "invite_code": code, "role": "veterinarian", "name": "Dr Lapse",
        "licence": {"licence_number": f"MEWA-{uuid.uuid4().hex[:6]}", "issuing_authority": "MEWA", "expires_on": EXPIRES_ON}})
    assert r.status_code == 201, r.text
    ident = auth.IDENTITY_REPO.get_by_email(email)
    auth.IDENTITY_REPO.upsert(dataclasses.replace(ident, tenant_id=T))
    admin = _signin(f"{admin_id}@d2g.test")
    lid = next(x["licence_id"] for x in admin.get("/api/admin/practitioners/licences").json() if x["actor_id"] == ident.user_id)
    v = admin.post(f"/api/admin/practitioners/licences/{lid}/verify", json={"method": "MANUAL_STAFF", "basis": "sighted"})
    assert v.status_code == 200, v.text
    return _signin(email)


@pytest.mark.parametrize("cell", list(CELLS))
def test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day(monkeypatch, cell):
    vet = _verified_vet(monkeypatch)
    instant, allowed = CELLS[cell]
    _pin(monkeypatch, api, instant)
    r = vet.post("/api/prescriptions", json=RX)
    if allowed:
        assert r.status_code == 200, r.text
    else:
        assert r.status_code == 403
        assert r.json()["detail"]["reason"] == "expired at 2031-03-11T00:00:00+03:00"


def test_the_licence_lapse_instant_is_riyadh_midnight():
    import licences
    lic = licences.VetLicence("l", "a", "N", "MEWA", datetime(2031, 3, 10).date(), BEFORE)
    assert lic.expires_at() == datetime(2031, 3, 10, 21, 0, tzinfo=timezone.utc)
    assert lic.expires_at().isoformat() == "2031-03-11T00:00:00+03:00"
