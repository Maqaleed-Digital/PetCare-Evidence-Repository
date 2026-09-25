"""FR-06 — the durable consultation record (AC-FR-06-04) and the fail-closed telemedicine gate
(AC-FR-06-05, dependency COUNSEL:REG-02_TELEMEDICINE) through the SERVED app (MVC-BUILD-RUNNER-001 U11).

The REG-02 determination is a governed counsel/Sponsor record with no served write path. One test
substitutes the repository's determination list IN-PROCESS to prove the gate reads it; that is test
setup, not counsel evidence, and no DEPENDENCY evidence is registered.
"""
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import consultations as consult  # noqa: E402
import main as api  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant, grant_practitioner_authority  # noqa: E402

pytestmark = pytest.mark.served_app
T_A, T_B = "t-fr06-alpha", "t-fr06-beta"


def _client(user_id, tenant, role):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@fr06.test", "pw", role, tenant_id=tenant)
    if role == "veterinarian":
        grant_practitioner_authority(user_id, tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@fr06.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _events(c, name, rid=None):
    ev = c.get("/audit/events/tenant", params={"limit": 5000}).json()["events"]
    return [e for e in ev if e["event_name"] == name and (rid is None or e["resource_id"] == rid)]


def _book(vet, owner_id, vet_id, **extra):
    return vet.post("/api/consultations", json={"pet_id": "pet-6", "owner_id": owner_id, "veterinarian_id": vet_id,
                                                **extra})


# --------------------------------------------------------------------------- AC-FR-06-04
def test_the_consultation_its_participants_and_outcome_are_recorded_and_audited():
    vet = _client("u-fr06-vet", T_A, "veterinarian")
    owner = _client("u-fr06-owner", T_A, "owner")
    other_vet = _client("u-fr06-vet-x", T_A, "veterinarian")
    r = _book(vet, "u-fr06-owner", "u-fr06-vet")
    assert r.status_code == 200, r.text
    sid = r.json()["session_id"]
    assert (r.json()["requested_by_actor_id"], r.json()["status"], r.json()["mode"]) == ("u-fr06-vet", "REQUESTED",
                                                                                         "IN_PERSON")
    assert owner.post(f"/api/consultations/{sid}/outcome", json={"outcome": "x"}).status_code == 403
    assert other_vet.post(f"/api/consultations/{sid}/outcome", json={"outcome": "x"}).status_code == 403
    done = vet.post(f"/api/consultations/{sid}/outcome", json={"outcome": "Otitis externa; drops prescribed"})
    assert done.status_code == 200, done.text
    body = done.json()
    assert body["status"] == "COMPLETED" and body["outcome"]["recorded_by_actor_id"] == "u-fr06-vet"
    assert (body["owner_id"], body["veterinarian_id"]) == ("u-fr06-owner", "u-fr06-vet")
    assert vet.post(f"/api/consultations/{sid}/outcome", json={"outcome": "again"}).status_code == 409
    assert [e["actor_id"] for e in _events(vet, "consultation.session.requested", sid)] == ["u-fr06-vet"]
    assert [e["actor_id"] for e in _events(vet, "consultation.outcome.recorded", sid)] == ["u-fr06-vet"]
    mine = owner.get("/api/consultations").json()["consultations"]
    assert [c["outcome"]["outcome"] for c in mine if c["session_id"] == sid] == ["Otitis externa; drops prescribed"]


def test_participants_must_be_identities_of_the_tenant_in_their_roles():
    vet = _client("u-fr06-vet2", T_A, "veterinarian")
    _client("u-fr06-owner-b", T_B, "owner")
    _client("u-fr06-owner2", T_A, "owner")
    assert _book(vet, "u-fr06-owner-b", "u-fr06-vet2").status_code == 400   # another tenant's owner
    assert _book(vet, "u-fr06-owner2", "u-fr06-owner2").status_code == 400  # an owner as the vet
    assert _book(vet, "nobody", "u-fr06-vet2").status_code == 400
    assert _book(vet, "u-fr06-owner2", "u-fr06-vet2", tenant_id=T_B).status_code == 403  # body tenant != session


def test_a_consultation_is_invisible_and_immovable_across_tenants():
    vet = _client("u-fr06-vet3", T_A, "veterinarian")
    _client("u-fr06-owner3", T_A, "owner")
    vet_b = _client("u-fr06-vet3b", T_B, "veterinarian")
    sid = _book(vet, "u-fr06-owner3", "u-fr06-vet3").json()["session_id"]
    assert vet_b.get(f"/api/consultations/{sid}").status_code == 404
    assert vet_b.post(f"/api/consultations/{sid}/outcome", json={"outcome": "x"}).status_code == 404
    assert sid not in [c["session_id"] for c in vet_b.get("/api/consultations").json()["consultations"]]
    assert not _events(vet_b, "consultation.session.requested", sid)


# --------------------------------------------------------------------------- AC-FR-06-05
def test_remote_consultation_is_not_offered_until_the_counsel_determination_is_recorded(monkeypatch):
    vet = _client("u-fr06-vet4", T_A, "veterinarian")
    _client("u-fr06-owner4", T_A, "owner")
    gate = vet.get("/api/consultations/remote/availability").json()
    assert gate["offered"] is False and gate["dependency"] == "COUNSEL:REG-02_TELEMEDICINE"
    r = _book(vet, "u-fr06-owner4", "u-fr06-vet4", mode="REMOTE_VIDEO")
    assert r.status_code == 403 and r.json()["detail"]["error"] == "REMOTE_CONSULTATION_NOT_OFFERED"
    assert _events(vet, "consultation.remote.refused")[-1]["actor_id"] == "u-fr06-vet4"
    assert _book(vet, "u-fr06-owner4", "u-fr06-vet4").status_code == 200  # in person is unaffected
    now = datetime.now(timezone.utc)
    lawful = consult.RegulatoryDetermination("d1", consult.REG02_TELEMEDICINE, consult.LAWFUL, "video, licensed vet",
                                             "counsel memo ref", "counsel", now - timedelta(days=1))
    monkeypatch.setattr(api.CONSULTATION_REPO, "_determinations", [lawful])
    assert vet.get("/api/consultations/remote/availability").json()["offered"] is True
    assert _book(vet, "u-fr06-owner4", "u-fr06-vet4", mode="REMOTE_VIDEO").status_code == 200
    withdrawn = consult.RegulatoryDetermination("d2", consult.REG02_TELEMEDICINE, consult.NOT_LAWFUL, "-", "ref 2",
                                                "counsel", now)
    monkeypatch.setattr(api.CONSULTATION_REPO, "_determinations", [lawful, withdrawn])
    assert _book(vet, "u-fr06-owner4", "u-fr06-vet4", mode="REMOTE_VIDEO").status_code == 403
