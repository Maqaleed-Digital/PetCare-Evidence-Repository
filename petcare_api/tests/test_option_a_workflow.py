"""Option A — intake, veterinarian verification, dispense, end to end.

The pilot workflow FR-14/FR-27 exist for, proven against the SERVED application
(`main.app`) rather than against a FastAPI app assembled by the test. A suite
that builds its own app proves the routers work and says nothing about whether
anything is reachable from the process that actually runs — which is the defect
`test_served_app_reachability.py` exists to catch, and the reason every test
here goes through the same `TestClient(api.app)`.

WHAT THIS SUITE DOES NOT CLAIM. There is no pharmacy actor. `pharmacy` is not an
authorization principal in this estate (PHARMACY_ROLE=REMOVE, W0-D) and
dispensing fails closed to VETERINARIAN pending a regulatory fact the estate
does not hold (REQ-DISP-AUTH-FAILCLOSED). So the dispensing step below is
performed by a veterinarian, which is the governed actor that exists — not by a
pharmacy operator, which is not one. Nothing here should be read as evidence
that an external pharmacy can operate this workflow.
"""
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
from prescriptions import (  # noqa: E402
    STATUS_DISPENSED,
    STATUS_ISSUED,
    STATUS_VET_VERIFIED,
)
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

client = TestClient(api.app)

T_A = "t-opta-alpha"
T_B = "t-opta-beta"

#: The smallest thing a PDF reader accepts. Real bytes, not a string that
#: happens to be allowlisted — the validator checks the declared type, and a
#: test that never sends a body cannot show the size rule working.
PDF_BYTES = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n"


def _login(role: str, email: str, tenant: str) -> None:
    ensure_tenant(tenant)
    auth.seed_user("u-" + email, email, "pw", role, tenant_id=tenant)
    r = client.post("/api/auth/sign-in", json={"email": email, "password": "pw"})
    assert r.status_code == 200, r.text
    client.cookies.set("petcare_session", r.cookies["petcare_session"])


def _logout() -> None:
    client.cookies.clear()


def _issue(tenant: str) -> dict:
    r = client.post(
        "/api/prescriptions",
        json={"pet_id": "pet-1", "session_id": "sess-1", "tenant_id": tenant,
              "clinic_id": "clinic-1", "medication_name": "amoxicillin",
              "dosage": "50mg", "instructions": "twice daily for 7 days"},
    )
    assert r.status_code == 200, r.text
    return r.json()


@pytest.fixture(autouse=True)
def _clean():
    _logout()
    yield
    _logout()


# ---------------------------------------------------------------------------
# A — the happy path
# ---------------------------------------------------------------------------
def test_a_upload_then_verify_then_dispense():
    _login(api.ROLE_VETERINARIAN, "vet-happy@t", T_A)
    rx = _issue(T_A)
    rx_id = rx["prescription_id"]
    assert rx["status"] == STATUS_ISSUED
    # The actor is server-derived: the record names the signed-in vet, and no
    # request above supplied an actor id at all.
    assert rx["issuing_vet_id"] == "u-vet-happy@t"

    up = client.post(
        f"/api/prescriptions/{rx_id}/documents",
        files={"file": ("scan.pdf", PDF_BYTES, "application/pdf")},
    )
    assert up.status_code == 200, up.text
    doc_id = up.json()["document_id"]
    assert up.json()["byte_size"] == len(PDF_BYTES)

    v = client.post(f"/api/prescriptions/{rx_id}/verify")
    assert v.status_code == 200, v.text
    assert v.json()["status"] == STATUS_VET_VERIFIED
    assert v.json()["verified_at"] is not None
    assert v.json()["verified_by_vet_id"] == "u-vet-happy@t"

    # The queue the dispensing screen reads now contains it.
    q = client.get("/api/prescriptions/queue/awaiting-dispense")
    assert q.status_code == 200, q.text
    assert rx_id in [row["prescription_id"] for row in q.json()]

    d = client.post(f"/api/prescriptions/{rx_id}/dispense")
    assert d.status_code == 200, d.text
    assert d.json()["status"] == STATUS_DISPENSED
    assert d.json()["dispensed_at"] is not None

    # And it leaves the queue, because the queue is computed from state rather
    # than from a flag something has to remember to clear.
    q2 = client.get("/api/prescriptions/queue/awaiting-dispense")
    assert rx_id not in [row["prescription_id"] for row in q2.json()]

    # The document is still retrievable, and served as a download.
    got = client.get(f"/api/prescriptions/{rx_id}/documents/{doc_id}")
    assert got.status_code == 200
    assert got.content == PDF_BYTES
    assert got.headers["content-type"].startswith("application/octet-stream")
    assert "attachment" in got.headers["content-disposition"]


def test_a2_the_transition_ledger_records_every_move():
    _login(api.ROLE_VETERINARIAN, "vet-ledger@t", T_A)
    rx_id = _issue(T_A)["prescription_id"]
    client.post(f"/api/prescriptions/{rx_id}/verify")
    client.post(f"/api/prescriptions/{rx_id}/dispense")

    t = client.get(f"/api/prescriptions/{rx_id}/transitions")
    assert t.status_code == 200, t.text
    moves = [(row["from_status"], row["to_status"]) for row in t.json()]
    assert moves == [
        (None, STATUS_ISSUED),
        (STATUS_ISSUED, STATUS_VET_VERIFIED),
        (STATUS_VET_VERIFIED, STATUS_DISPENSED),
    ], moves
    # Every entry is attributed to the session's identity, not to a header.
    assert {row["actor_id"] for row in t.json()} == {"u-vet-ledger@t"}


# ---------------------------------------------------------------------------
# C — tenant isolation
# ---------------------------------------------------------------------------
def test_c_another_tenant_cannot_read_the_prescription():
    _login(api.ROLE_VETERINARIAN, "vet-owner-a@t", T_A)
    rx_id = _issue(T_A)["prescription_id"]
    _logout()

    _login(api.ROLE_VETERINARIAN, "vet-intruder-b@t", T_B)
    r = client.get(f"/api/prescriptions/{rx_id}")
    # 404, not 403: a 403 would confirm the record exists to a caller who may
    # not read it, which is a working cross-tenant enumeration oracle.
    assert r.status_code == 404, f"cross-tenant read succeeded: {r.status_code}"


def test_c2_another_tenant_cannot_verify_or_dispense():
    _login(api.ROLE_VETERINARIAN, "vet-owner-a2@t", T_A)
    rx_id = _issue(T_A)["prescription_id"]
    _logout()

    _login(api.ROLE_VETERINARIAN, "vet-intruder-b2@t", T_B)
    assert client.post(f"/api/prescriptions/{rx_id}/verify").status_code == 404
    assert client.post(f"/api/prescriptions/{rx_id}/dispense").status_code == 404
    _logout()

    # And the record is untouched — the refusal was a refusal, not a partial
    # write that happened to return an error.
    _login(api.ROLE_VETERINARIAN, "vet-owner-a2b@t", T_A)
    assert client.get(f"/api/prescriptions/{rx_id}").json()["status"] == STATUS_ISSUED


def test_c3_the_queue_is_scoped_to_the_callers_tenant():
    _login(api.ROLE_VETERINARIAN, "vet-q-a@t", T_A)
    rx_a = _issue(T_A)["prescription_id"]
    client.post(f"/api/prescriptions/{rx_a}/verify")
    _logout()

    _login(api.ROLE_VETERINARIAN, "vet-q-b@t", T_B)
    q = client.get("/api/prescriptions/queue/awaiting-dispense")
    assert q.status_code == 200
    assert rx_a not in [row["prescription_id"] for row in q.json()], (
        "a verified prescription leaked into another tenant's queue"
    )


def test_c4_a_document_cannot_be_read_across_tenants():
    _login(api.ROLE_VETERINARIAN, "vet-doc-a@t", T_A)
    rx_id = _issue(T_A)["prescription_id"]
    up = client.post(
        f"/api/prescriptions/{rx_id}/documents",
        files={"file": ("scan.pdf", PDF_BYTES, "application/pdf")},
    )
    doc_id = up.json()["document_id"]
    _logout()

    _login(api.ROLE_VETERINARIAN, "vet-doc-b@t", T_B)
    r = client.get(f"/api/prescriptions/{rx_id}/documents/{doc_id}")
    assert r.status_code == 404, f"cross-tenant document read: {r.status_code}"


# ---------------------------------------------------------------------------
# D — authorization
# ---------------------------------------------------------------------------
def test_d_an_owner_may_not_issue_verify_or_upload():
    _login(api.ROLE_VETERINARIAN, "vet-for-owner@t", T_A)
    rx_id = _issue(T_A)["prescription_id"]
    _logout()

    _login(api.ROLE_OWNER, "owner-denied@t", T_A)
    assert client.post(
        "/api/prescriptions",
        json={"pet_id": "p", "session_id": "s", "tenant_id": T_A,
              "medication_name": "m", "dosage": "d", "instructions": "i"},
    ).status_code == 403
    assert client.post(f"/api/prescriptions/{rx_id}/verify").status_code == 403
    assert client.post(
        f"/api/prescriptions/{rx_id}/documents",
        files={"file": ("scan.pdf", PDF_BYTES, "application/pdf")},
    ).status_code == 403


def test_d2_an_unauthenticated_caller_reaches_nothing():
    _logout()
    for method, path in (
        ("post", "/api/prescriptions/x/verify"),
        ("post", "/api/prescriptions/x/dispense"),
        ("get", "/api/prescriptions/queue/awaiting-dispense"),
        ("get", "/api/prescriptions/x"),
    ):
        r = getattr(client, method)(path)
        assert r.status_code == 401, f"{path} answered {r.status_code} with no session"


def test_d3_a_client_header_cannot_confer_verification_authority():
    _login(api.ROLE_VETERINARIAN, "vet-hdr-src@t", T_A)
    rx_id = _issue(T_A)["prescription_id"]
    _logout()

    _login(api.ROLE_OWNER, "owner-hdr-v@t", T_A)
    r = client.post(
        f"/api/prescriptions/{rx_id}/verify",
        headers={"X-Petcare-Role": api.ROLE_VETERINARIAN,
                 "X-Actor-Id": "u-vet-hdr-src@t"},
    )
    assert r.status_code == 403, "a client header conferred verification authority"


# ---------------------------------------------------------------------------
# E — the verification gate
# ---------------------------------------------------------------------------
def test_e_an_unverified_prescription_is_not_in_the_queue_and_is_not_dispensable():
    _login(api.ROLE_VETERINARIAN, "vet-gate@t", T_A)
    rx_id = _issue(T_A)["prescription_id"]

    q = client.get("/api/prescriptions/queue/awaiting-dispense")
    assert rx_id not in [row["prescription_id"] for row in q.json()]

    d = client.post(f"/api/prescriptions/{rx_id}/dispense")
    assert d.status_code == 409, d.text
    assert client.get(f"/api/prescriptions/{rx_id}").json()["status"] == STATUS_ISSUED


def test_e2_a_prescription_cannot_be_verified_twice():
    _login(api.ROLE_VETERINARIAN, "vet-twice-v@t", T_A)
    rx_id = _issue(T_A)["prescription_id"]
    assert client.post(f"/api/prescriptions/{rx_id}/verify").status_code == 200
    assert client.post(f"/api/prescriptions/{rx_id}/verify").status_code == 409


# ---------------------------------------------------------------------------
# G — upload validation
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "filename,content_type,payload,why",
    [
        ("evil.svg", "image/svg+xml",
         b"<svg xmlns='http://www.w3.org/2000/svg'><script>alert(1)</script></svg>",
         "svg executes script in the application origin"),
        ("evil.html", "text/html", b"<script>alert(1)</script>",
         "html executes script in the application origin"),
        ("shell.sh", "application/x-sh", b"#!/bin/sh\nrm -rf /\n",
         "an executable is not a prescription attachment"),
        ("empty.pdf", "application/pdf", b"", "an empty document is not a record"),
    ],
)
def test_g_the_upload_allowlist_refuses(filename, content_type, payload, why):
    _login(api.ROLE_VETERINARIAN, "vet-upload-bad@t", T_A)
    rx_id = _issue(T_A)["prescription_id"]
    r = client.post(
        f"/api/prescriptions/{rx_id}/documents",
        files={"file": (filename, payload, content_type)},
    )
    assert r.status_code == 400, f"{why}: accepted with {r.status_code}"
    # And nothing was recorded, so a rejected upload leaves no dangling metadata.
    listing = client.get(f"/api/prescriptions/{rx_id}/documents")
    assert listing.json() == []


def test_g2_an_oversized_document_is_refused():
    _login(api.ROLE_VETERINARIAN, "vet-upload-big@t", T_A)
    rx_id = _issue(T_A)["prescription_id"]
    from prescription_documents import MAX_DOCUMENT_BYTES

    r = client.post(
        f"/api/prescriptions/{rx_id}/documents",
        files={"file": ("big.pdf", b"%PDF" + b"\0" * MAX_DOCUMENT_BYTES,
                        "application/pdf")},
    )
    assert r.status_code == 400, r.status_code


def test_g3_a_traversing_filename_does_not_choose_a_path():
    """The filename is metadata. The storage key is server-generated.

    ARMED by asserting the stored key is unrelated to the submitted name: if a
    future edit ever derived the key from the filename, the traversal sequence
    would appear in it and this fails.
    """
    _login(api.ROLE_VETERINARIAN, "vet-traversal@t", T_A)
    rx_id = _issue(T_A)["prescription_id"]
    r = client.post(
        f"/api/prescriptions/{rx_id}/documents",
        files={"file": ("../../../../etc/passwd", PDF_BYTES, "application/pdf")},
    )
    assert r.status_code == 200, r.text
    doc = api.PRESCRIPTION_REPO.get_document(r.json()["document_id"], tenant_id=T_A)
    assert ".." not in doc.storage_key
    assert "etc" not in doc.storage_key
    assert "passwd" not in doc.storage_key


# ---------------------------------------------------------------------------
# J — audit
# ---------------------------------------------------------------------------
def test_j_every_step_is_audited_with_a_server_derived_actor():
    _login(api.ROLE_VETERINARIAN, "vet-audit@t", T_A)
    rx_id = _issue(T_A)["prescription_id"]
    up = client.post(
        f"/api/prescriptions/{rx_id}/documents",
        files={"file": ("scan.pdf", PDF_BYTES, "application/pdf")},
        headers={"X-Actor-Id": "somebody-else-entirely"},
    )
    doc_id = up.json()["document_id"]
    client.post(f"/api/prescriptions/{rx_id}/verify")
    client.post(f"/api/prescriptions/{rx_id}/dispense")

    # Scoped to THIS prescription and THIS document. The in-memory audit log is
    # shared across the module, so a filter on resource_type alone would pick up
    # every other test's uploads and the actor assertion below would be about
    # them instead.
    events = [e for e in api.AUDIT_REPO.all_events()
              if e.get("resource_id") in (rx_id, doc_id)]
    names = {e["event_name"] for e in events}
    assert {"prescription.issued", "prescription.document_uploaded",
            "prescription.vet_verified", "prescription.dispensed"} <= names, names

    # The header supplied above named a different actor. It was ignored.
    actors = {e["actor_id"] for e in events}
    assert actors == {"u-vet-audit@t"}, actors
    assert "somebody-else-entirely" not in actors


def test_j2_a_refused_transition_is_audited_as_denied():
    _login(api.ROLE_VETERINARIAN, "vet-audit-deny@t", T_A)
    rx_id = _issue(T_A)["prescription_id"]
    assert client.post(f"/api/prescriptions/{rx_id}/dispense").status_code == 409

    denials = [e for e in api.AUDIT_REPO.all_events()
               if e.get("resource_id") == rx_id
               and e["event_name"] == "prescription.dispense_denied"]
    assert denials, "a refused dispense left no audit trace"
    assert denials[0]["action_result"] == "denied"
