"""MVC-EPC-D-001 D2g — X-22 cell-sensitive lapse probe (finding D2G-X22-PERTURBATION-BREADTH, Sponsor R18 step 2).

Driven by the CURRENT clock (the D2g matrix pins it per cell), it asserts only the allow/refuse outcome of a clinical act:
  - a licence that expired on the Asia/Riyadh "yesterday" is refused now;
  - a licence valid through the Asia/Riyadh "today" is allowed now.
Under the governed rule both hold at every instant. Under a UTC-midnight lapse the first is wrongly ALLOWED exactly when the
Riyadh wall clock is before 03:00 (the Riyadh and UTC dates differ), and nowhere else — so a UTC reversion fails this probe
in the 00:00–02:59 Riyadh cells only, and passes in the others. No reason string is asserted.
"""
import dataclasses
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import licences  # noqa: E402
import main as api  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

pytestmark = pytest.mark.served_app
T = "t-d2g-x22-probe"
PW = "Pw-long-enough-1"
RX = {"pet_id": "p1", "session_id": "s1", "medication_name": "Amoxicillin", "dosage": "50mg", "instructions": "bid"}


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


@pytest.mark.parametrize("valid_through,allowed", [("riyadh-yesterday", False), ("riyadh-today", True)])
def test_a_clinical_act_now_follows_the_riyadh_calendar(monkeypatch, valid_through, allowed):
    now = datetime.now(timezone.utc)
    today = licences.licence_calendar_date(now)
    expires_on = today - timedelta(days=1) if valid_through == "riyadh-yesterday" else today
    earlier = now - timedelta(days=3)                                  # registration and verification, licence then valid
    ensure_tenant(T)
    _pin(monkeypatch, auth, earlier)
    _pin(monkeypatch, api, earlier)
    admin_id = f"u-probe-admin-{uuid.uuid4().hex[:6]}"
    auth.seed_user(admin_id, f"{admin_id}@probe.test", PW, "platform_admin", tenant_id=T)
    code = f"PROBE-{uuid.uuid4().hex[:8]}"
    auth.seed_invite_code(code, "veterinarian")
    email = f"vet-{uuid.uuid4().hex[:8]}@probe.test"
    r = TestClient(api.app).post("/api/auth/register", json={
        "email": email, "password": PW, "invite_code": code, "role": "veterinarian", "name": "Dr Probe",
        "licence": {"licence_number": f"MEWA-{uuid.uuid4().hex[:6]}", "issuing_authority": "MEWA", "expires_on": expires_on.isoformat()}})
    assert r.status_code == 201, r.text
    ident = auth.IDENTITY_REPO.get_by_email(email)
    auth.IDENTITY_REPO.upsert(dataclasses.replace(ident, tenant_id=T))
    admin = _signin(f"{admin_id}@probe.test")
    lid = next(x["licence_id"] for x in admin.get("/api/admin/practitioners/licences").json() if x["actor_id"] == ident.user_id)
    assert admin.post(f"/api/admin/practitioners/licences/{lid}/verify", json={"method": "MANUAL_STAFF", "basis": "sighted"}).status_code == 200
    vet = _signin(email)
    _pin(monkeypatch, api, now)                                        # the act happens NOW (the matrix's pinned cell)
    assert vet.post("/api/prescriptions", json=RX).status_code == (200 if allowed else 403)
