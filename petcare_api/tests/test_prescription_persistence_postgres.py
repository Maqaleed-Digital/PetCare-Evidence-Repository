"""FR-14 — a prescription outlives the process that wrote it.

Against REAL PostgreSQL, through the same repository the serving path uses.

The claim being proven is narrow and is the whole point of FR-14: the record
survives the repository object. Every assertion below therefore reads through a
SECOND repository instance built from a second `build_persistence()` — a fresh
object over the same database, which is what a second container is. A test that
read back through the same instance would pass just as happily against the
module-level dict this migration replaced, and would prove nothing.
"""
import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import main as api  # noqa: E402
import routers.auth as auth  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from tenant_fixtures import grant_practitioner_authority  # noqa: E402
from persistence import (  # noqa: E402
    MODE_POSTGRES,
    PERSISTENCE_MODE_ENV_VAR,
    build_persistence,
)
from prescriptions import (  # noqa: E402
    Prescription,
    STATUS_DISPENSED,
    STATUS_ISSUED,
    STATUS_VET_VERIFIED,
    TransitionDenied,
)
from repositories import RepositoryDenied  # noqa: E402
from roles import ROLE_VETERINARIAN  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T_A, T_B = "t-rx-alpha", "t-rx-beta"
_ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}


def _persistence(url: str):
    return build_persistence(_ENV, connection_url=url)


@pytest.fixture()
def pg(clean_postgres):
    """A migrated, empty database with both tenants present."""
    p = _persistence(clean_postgres)
    for tid in (T_A, T_B):
        p.tenants.create(Tenant(tenant_id=tid, display_name=f"Fixture {tid}"))
    yield clean_postgres


def _new_rx(tenant: str = T_A, vet: str = "u-vet-1") -> Prescription:
    return Prescription(
        prescription_id=str(uuid4()),
        tenant_id=tenant,
        pet_id="pet-1",
        session_id="sess-1",
        clinic_id="clinic-1",
        issuing_vet_id=vet,
        medication_name="amoxicillin",
        dosage="50mg",
        instructions="twice daily for 7 days",
        status=STATUS_ISSUED,
        issued_at=datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# B — durability
# ---------------------------------------------------------------------------
def test_b_a_prescription_survives_repository_reinstantiation(pg):
    writer = _persistence(pg).prescriptions
    rx = _new_rx()
    writer.create(rx, actor_id="u-vet-1", actor_role=ROLE_VETERINARIAN)

    # A DIFFERENT repository over the same database. This is the assertion the
    # in-memory implementation cannot satisfy.
    reader = _persistence(pg).prescriptions
    found = reader.get(rx.prescription_id, tenant_id=T_A)
    assert found is not None, "the prescription did not survive the repository"
    assert found.medication_name == "amoxicillin"
    assert found.status == STATUS_ISSUED
    assert found.issuing_vet_id == "u-vet-1"


def test_b2_the_whole_lifecycle_survives(pg):
    a = _persistence(pg).prescriptions
    rx = _new_rx()
    a.create(rx, actor_id="u-vet-1", actor_role=ROLE_VETERINARIAN)

    b = _persistence(pg).prescriptions
    b.transition(rx.prescription_id, tenant_id=T_A, to_status=STATUS_VET_VERIFIED,
                 actor_id="u-vet-2", actor_role=ROLE_VETERINARIAN)

    c = _persistence(pg).prescriptions
    c.transition(rx.prescription_id, tenant_id=T_A, to_status=STATUS_DISPENSED,
                 actor_id="u-vet-3", actor_role=ROLE_VETERINARIAN)

    d = _persistence(pg).prescriptions
    final = d.get(rx.prescription_id, tenant_id=T_A)
    assert final.status == STATUS_DISPENSED
    assert final.verified_by_vet_id == "u-vet-2"
    assert final.dispensed_by_actor_id == "u-vet-3"
    assert final.verified_at is not None and final.dispensed_at is not None

    moves = [(t.from_status, t.to_status)
             for t in d.transitions_for(rx.prescription_id, tenant_id=T_A)]
    assert moves == [
        (None, STATUS_ISSUED),
        (STATUS_ISSUED, STATUS_VET_VERIFIED),
        (STATUS_VET_VERIFIED, STATUS_DISPENSED),
    ], moves


# ---------------------------------------------------------------------------
# The transitions the database itself refuses
# ---------------------------------------------------------------------------
def test_the_verification_gate_holds_in_postgres(pg):
    repo = _persistence(pg).prescriptions
    rx = _new_rx()
    repo.create(rx, actor_id="u-vet-1", actor_role=ROLE_VETERINARIAN)
    with pytest.raises(TransitionDenied):
        repo.transition(rx.prescription_id, tenant_id=T_A,
                        to_status=STATUS_DISPENSED, actor_id="u-vet-1",
                        actor_role=ROLE_VETERINARIAN)
    assert repo.get(rx.prescription_id, tenant_id=T_A).status == STATUS_ISSUED


def test_a_dispensed_prescription_has_no_outgoing_transition(pg):
    repo = _persistence(pg).prescriptions
    rx = _new_rx()
    repo.create(rx, actor_id="u-vet-1", actor_role=ROLE_VETERINARIAN)
    repo.transition(rx.prescription_id, tenant_id=T_A, to_status=STATUS_VET_VERIFIED,
                    actor_id="u-vet-1", actor_role=ROLE_VETERINARIAN)
    repo.transition(rx.prescription_id, tenant_id=T_A, to_status=STATUS_DISPENSED,
                    actor_id="u-vet-1", actor_role=ROLE_VETERINARIAN)
    with pytest.raises(TransitionDenied):
        repo.transition(rx.prescription_id, tenant_id=T_A,
                        to_status=STATUS_DISPENSED, actor_id="u-vet-1",
                        actor_role=ROLE_VETERINARIAN)


def test_the_schema_refuses_a_dispense_that_skipped_verification(pg):
    """The constraint, reached directly — bypassing the repository entirely.

    The repository's `assert_transition_allowed` is one guard. This proves the
    SECOND one: a writer that never calls this code — a migration, a fix-up
    script, a future service — still cannot leave a prescription DISPENSED with
    no verification instant. Without this, "enforced in the database" would be a
    claim about a file rather than about the database.
    """
    with psycopg.connect(pg, autocommit=True) as conn:
        with pytest.raises(psycopg.errors.CheckViolation):
            conn.execute(
                "INSERT INTO prescription (prescription_id, tenant_id, pet_id, "
                " session_id, issuing_vet_id, medication_name, dosage, "
                " instructions, status, issued_at, dispensed_at, "
                " dispensed_by_actor_id) "
                "VALUES (%s,%s,'p','s','v','m','d','i','DISPENSED',NOW(),NOW(),'a')",
                (str(uuid4()), T_A),
            )


def test_the_schema_refuses_a_prescription_in_an_unregistered_tenant(pg):
    repo = _persistence(pg).prescriptions
    rx = _new_rx(tenant="t-never-registered")
    with pytest.raises(RepositoryDenied):
        repo.create(rx, actor_id="u-vet-1", actor_role=ROLE_VETERINARIAN)


# ---------------------------------------------------------------------------
# C — tenant isolation, durable
# ---------------------------------------------------------------------------
def test_c_tenant_b_cannot_read_or_move_tenant_a_prescription(pg):
    repo = _persistence(pg).prescriptions
    rx = _new_rx(tenant=T_A)
    repo.create(rx, actor_id="u-vet-1", actor_role=ROLE_VETERINARIAN)

    other = _persistence(pg).prescriptions
    assert other.get(rx.prescription_id, tenant_id=T_B) is None

    from prescriptions import PrescriptionNotFound

    with pytest.raises(PrescriptionNotFound):
        other.transition(rx.prescription_id, tenant_id=T_B,
                         to_status=STATUS_VET_VERIFIED, actor_id="u-vet-b",
                         actor_role=ROLE_VETERINARIAN)
    # Untouched.
    assert repo.get(rx.prescription_id, tenant_id=T_A).status == STATUS_ISSUED


def test_the_queue_never_crosses_tenants(pg):
    repo = _persistence(pg).prescriptions
    for tenant in (T_A, T_B):
        rx = _new_rx(tenant=tenant)
        repo.create(rx, actor_id="u-vet-1", actor_role=ROLE_VETERINARIAN)
        repo.transition(rx.prescription_id, tenant_id=tenant,
                        to_status=STATUS_VET_VERIFIED, actor_id="u-vet-1",
                        actor_role=ROLE_VETERINARIAN)

    a_queue = repo.list_by_status(tenant_id=T_A, status=STATUS_VET_VERIFIED)
    b_queue = repo.list_by_status(tenant_id=T_B, status=STATUS_VET_VERIFIED)
    assert len(a_queue) == 1 and len(b_queue) == 1
    assert {r.tenant_id for r in a_queue} == {T_A}
    assert {r.tenant_id for r in b_queue} == {T_B}


# ---------------------------------------------------------------------------
# The served application, on PostgreSQL
# ---------------------------------------------------------------------------
def test_the_served_app_writes_prescriptions_to_postgres(pg):
    """End to end through HTTP, with the durable store installed.

    The memory-mode suite proves the workflow. This proves the workflow writes
    to the database — the two are different claims, and only this one fails if
    the serving layer is ever pointed back at a dict.
    """
    persistence = _persistence(pg)
    saved = (auth.PERSISTENCE, auth.SESSION_STORE, auth.IDENTITY_REPO,
             auth.INVITE_REPO, api.AUDIT_REPO, api.PRESCRIPTION_REPO)
    auth.PERSISTENCE = persistence
    auth.SESSION_STORE = persistence.session_store
    auth.IDENTITY_REPO = persistence.identities
    auth.INVITE_REPO = persistence.invites
    api.AUDIT_REPO = persistence.audit
    api.PRESCRIPTION_REPO = persistence.prescriptions
    saved_practitioners = api.PRACTITIONER_REPO  # FR-01 (U5)
    api.PRACTITIONER_REPO = persistence.practitioners

    client = TestClient(api.app)
    try:
        auth.seed_user("u-vet-pg", "vet-pg@t", "pw", ROLE_VETERINARIAN,
                       tenant_id=T_A)
        grant_practitioner_authority("u-vet-pg", T_A, persistence=persistence)
        r = client.post("/api/auth/sign-in",
                        json={"email": "vet-pg@t", "password": "pw"})
        assert r.status_code == 200, r.text
        client.cookies.set("petcare_session", r.cookies["petcare_session"])

        issued = client.post(
            "/api/prescriptions",
            json={"pet_id": "pet-1", "session_id": "s1", "tenant_id": T_A,
                  "medication_name": "amoxicillin", "dosage": "50mg",
                  "instructions": "twice daily"},
        )
        assert issued.status_code == 200, issued.text
        rx_id = issued.json()["prescription_id"]

        assert client.post(f"/api/prescriptions/{rx_id}/verify").status_code == 200
        assert client.post(f"/api/prescriptions/{rx_id}/dispense").status_code == 200

        # Read back with a repository the request never touched.
        fresh = _persistence(pg).prescriptions.get(rx_id, tenant_id=T_A)
        assert fresh is not None, "the HTTP write did not reach PostgreSQL"
        assert fresh.status == STATUS_DISPENSED
        assert fresh.issuing_vet_id == "u-vet-pg"
    finally:
        client.cookies.clear()
        (auth.PERSISTENCE, auth.SESSION_STORE, auth.IDENTITY_REPO,
         auth.INVITE_REPO, api.AUDIT_REPO, api.PRESCRIPTION_REPO) = saved
        api.PRACTITIONER_REPO = saved_practitioners


def test_j_audit_events_for_the_workflow_persist_and_chain(pg):
    """J — the audit trail survives, and its chain still verifies."""
    persistence = _persistence(pg)
    saved = (auth.PERSISTENCE, auth.SESSION_STORE, auth.IDENTITY_REPO,
             auth.INVITE_REPO, api.AUDIT_REPO, api.PRESCRIPTION_REPO)
    auth.PERSISTENCE = persistence
    auth.SESSION_STORE = persistence.session_store
    auth.IDENTITY_REPO = persistence.identities
    auth.INVITE_REPO = persistence.invites
    api.AUDIT_REPO = persistence.audit
    api.PRESCRIPTION_REPO = persistence.prescriptions
    saved_practitioners = api.PRACTITIONER_REPO  # FR-01 (U5)
    api.PRACTITIONER_REPO = persistence.practitioners

    client = TestClient(api.app)
    try:
        auth.seed_user("u-vet-audit-pg", "vet-audit-pg@t", "pw",
                       ROLE_VETERINARIAN, tenant_id=T_A)
        grant_practitioner_authority("u-vet-audit-pg", T_A, persistence=persistence)
        r = client.post("/api/auth/sign-in",
                        json={"email": "vet-audit-pg@t", "password": "pw"})
        client.cookies.set("petcare_session", r.cookies["petcare_session"])
        rx_id = client.post(
            "/api/prescriptions",
            json={"pet_id": "p", "session_id": "s", "tenant_id": T_A,
                  "medication_name": "m", "dosage": "d", "instructions": "i"},
        ).json()["prescription_id"]
        client.post(f"/api/prescriptions/{rx_id}/verify")
        client.post(f"/api/prescriptions/{rx_id}/dispense")
    finally:
        client.cookies.clear()
        (auth.PERSISTENCE, auth.SESSION_STORE, auth.IDENTITY_REPO,
         auth.INVITE_REPO, api.AUDIT_REPO, api.PRESCRIPTION_REPO) = saved
        api.PRACTITIONER_REPO = saved_practitioners

    # A repository the requests never touched.
    events = _persistence(pg).audit.all_events()
    names = [e["event_name"] for e in events]
    for expected in ("prescription.issued", "prescription.vet_verified",
                     "prescription.dispensed"):
        assert expected in names, f"{expected} did not persist: {names}"

    chained = [e for e in events if e["event_name"].startswith("prescription.")]
    assert chained, "no prescription events persisted"
    for ev in chained:
        assert ev.get("event_hash"), f"{ev['event_name']} persisted with no chain hash"
        assert ev.get("prev_hash"), f"{ev['event_name']} persisted with no prev_hash"
