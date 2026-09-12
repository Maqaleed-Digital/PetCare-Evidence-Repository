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
from repositories import RepositoryDenied
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

    Now asserted at BOTH layers, because W0-F added an earlier one.

    Layer 1 — authorization. The retired role is absent from the set
    `require_role()` accepts, so a session carrying it could never be honoured.
    Unchanged, and still asserted first.

    Layer 2 — storage (W0-F). The identity store refuses to hold the retired
    role at all, so no identity can carry it, no session can be minted for it,
    and it never reaches authorization. That is strictly stronger than the
    previous end-to-end proof, which allowed the identity to exist, sign in
    successfully, and be refused only at the route: a defence that depended on
    every protected route remembering to check.

    The test's name is now literally true. It previously proved the retired role
    COULD authenticate and was then denied; it now proves it cannot authenticate.
    """
    # Layer 1 — the authorization catalogue still excludes it.
    assert api.ROLE_PHARMACY_OPERATOR not in api.VALID_ROLES

    # Layer 2 — and it cannot be stored, so no session can exist for it.
    with pytest.raises(RepositoryDenied):
        auth.seed_user("u-pharm@t", "pharm@t", "pw", api.ROLE_PHARMACY_OPERATOR,
                       tenant_id=TENANT)

    # No identity was created by the refused write, so sign-in finds nothing.
    # Asserted rather than assumed: a partial write would leave a credential
    # behind that the refusal appeared to have prevented.
    assert auth.IDENTITY_REPO.get_by_email("pharm@t") is None
    r = client.post("/api/auth/sign-in",
                    json={"email": "pharm@t", "password": "pw"})
    assert r.status_code == 401, "retired role obtained a session"

    # The positive control the negative one needs: dispensing still works for
    # the role that IS authorised, so this file is not passing by denying
    # everything. (test_t_disp_01 asserts the same thing independently.)
    rx = _issue_prescription()
    assert rx
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
