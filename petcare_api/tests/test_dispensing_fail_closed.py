"""W0-D — REQ-DISP-AUTH-FAILCLOSED (BRD V3.2 §11.1).

The defect inverted the governed invariant: dispensing REQUIRED
ROLE_PHARMACY_OPERATOR and DENIED the veterinarian, using a role the
specification says must not exist in any environment.

Two dispensing acts remain deliberately unclassified pending a regulatory fact
the estate does not hold. Until a ratified professional-authority rule names
another actor class, they fail closed to VETERINARIAN. That is a default, not a
determination.

PATH PROOF: every test posts to the dispense route, so the guard is reached.
"""
import pytest
from fastapi.testclient import TestClient

import main as api
from routers import auth

client = TestClient(api.app)
TENANT = "t1"


def _login(role: str, email: str):
    auth.seed_user("u-" + email, email, "pw", role, tenant_id=TENANT)
    r = client.post("/api/auth/sign-in", json={"email": email, "password": "pw"})
    assert r.status_code == 200, r.text
    client.cookies.set("petcare_session", r.cookies["petcare_session"])


def _issue_prescription() -> str:
    """A veterinarian issues one, so there is something to dispense."""
    _login(api.ROLE_VETERINARIAN, "rx-writer@t")
    r = client.post(
        "/api/prescriptions",
        json={"pet_id": "p1", "session_id": "s1", "tenant_id": TENANT,
              "medication_name": "amoxicillin", "dosage": "50mg",
              "instructions": "twice daily for 7 days"},
        headers={"X-Actor-Id": "vet-1"},
    )
    assert r.status_code in (200, 201), r.text
    client.cookies.clear()
    return r.json()["prescription_id"]


def _dispense(rx_id: str):
    return client.post(f"/api/prescriptions/{rx_id}/dispense",
                       headers={"X-Actor-Id": "actor-1"})


def test_t_disp_03_non_veterinarian_is_denied_an_unclassified_act():
    """T-DISP-03 (ARMED) — an OWNER must not dispense."""
    rx = _issue_prescription()
    _login(api.ROLE_OWNER, "owner-disp@t")
    try:
        r = _dispense(rx)
        assert r.status_code == 403, f"non-veterinarian dispensed: {r.status_code}"
    finally:
        client.cookies.clear()


def test_t_disp_04_unknown_actor_class_is_denied():
    """T-DISP-04 — no session means no professional class, so DENY."""
    rx = _issue_prescription()
    r = _dispense(rx)
    assert r.status_code == 401


def test_t_disp_05_retired_pharmacy_operator_cannot_authenticate():
    """T-DISP-05 (ARMED) — PHARMACY_OPERATOR must not exist in any environment.

    A session minted for the retired role must be rejected by require_role,
    which is what "may never arrive as a role-catalogue migration" means in
    practice.
    """
    assert api.ROLE_PHARMACY_OPERATOR not in api.VALID_ROLES
    rx = _issue_prescription()
    _login(api.ROLE_PHARMACY_OPERATOR, "pharm@t")
    try:
        r = _dispense(rx)
        assert r.status_code == 403, "retired role was accepted as authority"
    finally:
        client.cookies.clear()


def test_t_disp_06_client_cannot_assert_professional_class():
    """T-DISP-06 (ARMED) — a header must not confer dispensing authority."""
    rx = _issue_prescription()
    _login(api.ROLE_OWNER, "owner-hdr@t")
    try:
        r = client.post(f"/api/prescriptions/{rx}/dispense",
                        headers={"X-Actor-Id": "a",
                                 "X-Petcare-Role": api.ROLE_VETERINARIAN})
        assert r.status_code == 403, "client header conferred dispensing authority"
    finally:
        client.cookies.clear()


def test_t_disp_01_veterinarian_positive_control():
    """Positive control — the veterinarian MAY dispense. Without this, denying
    everything would pass every negative test vacuously."""
    rx = _issue_prescription()
    _login(api.ROLE_VETERINARIAN, "vet-disp@t")
    try:
        r = _dispense(rx)
        assert r.status_code == 200, r.text
        assert r.json()["status"] == "DISPENSED"
    finally:
        client.cookies.clear()
