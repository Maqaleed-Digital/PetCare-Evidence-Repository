"""MVC-EPC-D-001 D3c — J-V3 (R21.4): the consultation workspace (CV-05). The consultation's OWN veterinarian opens its workspace
(consultation, patient, owner, the SOAP draft in force, structural templates) and saves SOAP drafts: insert-only versions, the
latest in force, unsigned, audited without the note's text. Another veterinarian's or another tenant's consultation is 404; an
owner has no workspace; a veterinarian without a practitioner authority in force cannot write. Templates are headings only."""
import os
import sys
import uuid

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
import soap_notes as soap  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant, grant_practitioner_authority  # noqa: E402

pytestmark = pytest.mark.served_app


def _client(user_id, tenant, role, name=None, authority=True):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@jv3.test", "pw", role, full_name=name or user_id, tenant_id=tenant)
    if role == "veterinarian" and authority:
        grant_practitioner_authority(user_id, tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@jv3.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


@pytest.fixture()
def w():
    tag = uuid.uuid4().hex[:6]
    t, other = f"t-d3c-jv3-{tag}", f"t-d3c-jv3-other-{tag}"
    w = {"t": t, "vet_id": f"u-v3-vet-{tag}", "owner_id": f"u-v3-own-{tag}"}
    w["vet"] = _client(w["vet_id"], t, "veterinarian")
    w["vet2"] = _client(f"u-v3-vet2-{tag}", t, "veterinarian")
    w["vet_other_tenant"] = _client(f"u-v3-vet3-{tag}", other, "veterinarian")
    w["owner"] = _client(w["owner_id"], t, "owner", name="Huda")
    w["pet"] = w["owner"].post("/api/pets", json={"name": "Luna", "species": "cat", "breed": "Siamese"}).json()["pet_id"]
    r = w["vet"].post("/api/consultations", json={"pet_id": w["pet"], "owner_id": w["owner_id"], "veterinarian_id": w["vet_id"]})
    assert r.status_code == 200, r.text
    w["sid"] = r.json()["session_id"]
    return w


def _save(c, sid, **sections):
    return c.put(f"/api/vet/consultations/{sid}/soap", json=sections)


def test_the_workspace_shows_the_consultation_patient_owner_and_templates(w):
    r = w["vet"].get(f"/api/vet/consultations/{w['sid']}/workspace")
    assert r.status_code == 200, r.text
    b = r.json()
    assert b["consultation"]["session_id"] == w["sid"] and b["consultation"]["status"] == "REQUESTED"
    assert b["pet"] == {"pet_id": w["pet"], "name": "Luna", "species": "cat", "breed": "Siamese"}
    assert b["owner_name"] == "Huda"
    assert b["soap"] is None and b["soap_versions"] == 0
    assert [t["template_id"] for t in b["templates"]] == ["SOAP_GENERAL", "SOAP_FOLLOW_UP"]
    assert b["remote"]["offered"] is False                                     # REG-02 not recorded: no video offered
    events = [e for e in api.AUDIT_REPO.query_events_for_tenant(w["t"], limit=500)
              if e["event_name"] == "consultation.workspace.viewed" and e["resource_id"] == w["sid"]]
    assert len(events) == 1 and events[0]["actor_id"] == w["vet_id"]


def test_drafts_are_versions_the_latest_is_in_force_and_unsigned(w):
    r1 = _save(w["vet"], w["sid"], template_id="SOAP_GENERAL", subjective="Limping for two days", objective="")
    assert r1.status_code == 200, r1.text
    assert r1.json()["status"] == "DRAFT" and r1.json()["template_id"] == "SOAP_GENERAL"
    r2 = _save(w["vet"], w["sid"], template_id="SOAP_GENERAL", subjective="Limping for two days",
               objective="Weight (kg): 4.2", assessment="Soft-tissue strain", plan="Rest")
    assert r2.status_code == 200, r2.text
    b = w["vet"].get(f"/api/vet/consultations/{w['sid']}/workspace").json()
    assert b["soap_versions"] == 2
    assert b["soap"]["draft_id"] == r2.json()["draft_id"]
    assert (b["soap"]["objective"], b["soap"]["assessment"], b["soap"]["plan"]) == ("Weight (kg): 4.2", "Soft-tissue strain", "Rest")
    assert b["soap"]["status"] == "DRAFT" and b["soap"]["saved_by_actor_id"] == w["vet_id"]
    saved = [e for e in api.AUDIT_REPO.query_events_for_tenant(w["t"], limit=500) if e["event_name"] == "consultation.soap_draft.saved"]
    assert {e["resource_id"] for e in saved} == {r1.json()["draft_id"], r2.json()["draft_id"]}
    assert not any("Limping" in str(e) for e in saved)                         # the note's text never enters the audit


def test_a_draft_does_not_complete_the_consultation_and_the_outcome_does(w):
    assert _save(w["vet"], w["sid"], subjective="Itching").status_code == 200
    assert [c["session_id"] for c in w["vet"].get("/api/vet/queue").json()["open_consultations"]] == [w["sid"]]
    assert w["vet"].post(f"/api/consultations/{w['sid']}/outcome", json={"outcome": "Flea allergy"}).status_code == 200
    b = w["vet"].get(f"/api/vet/consultations/{w['sid']}/workspace").json()
    assert b["consultation"]["status"] == "COMPLETED" and b["soap"]["subjective"] == "Itching"
    assert w["vet"].get("/api/vet/queue").json()["open_consultations"] == []


@pytest.mark.parametrize("body", [
    {},                                                                         # nothing written
    {"subjective": "   ", "plan": "\n"},                                        # whitespace is not a note
    {"subjective": "x" * (soap.MAX_SECTION + 1)},
    {"template_id": "SOAP_INVENTED", "subjective": "Itching"},
])
def test_an_invalid_draft_is_refused_and_changes_nothing(w, body):
    r = _save(w["vet"], w["sid"], **body)
    assert r.status_code == 400 and r.json()["detail"]["error"] == "SOAP_DRAFT_INVALID"
    assert w["vet"].get(f"/api/vet/consultations/{w['sid']}/workspace").json()["soap_versions"] == 0


def test_an_unknown_field_is_refused(w):
    assert _save(w["vet"], w["sid"], subjective="Itching", signed=True).status_code == 422


def test_only_the_consultations_own_veterinarian_has_its_workspace(w):
    for c in (w["vet2"], w["vet_other_tenant"]):
        assert c.get(f"/api/vet/consultations/{w['sid']}/workspace").status_code == 404
        assert _save(c, w["sid"], subjective="Intruder").status_code == 404
    assert w["vet"].get("/api/vet/consultations/not-a-session/workspace").status_code == 404
    assert w["owner"].get(f"/api/vet/consultations/{w['sid']}/workspace").status_code == 403
    assert _save(w["owner"], w["sid"], subjective="Owner").status_code == 403
    assert w["vet"].get(f"/api/vet/consultations/{w['sid']}/workspace").json()["soap_versions"] == 0


def test_writing_a_draft_needs_a_practitioner_authority_in_force(w):
    tag = uuid.uuid4().hex[:6]
    vet_id = f"u-v3-noauth-{tag}"
    vet = _client(vet_id, w["t"], "veterinarian", authority=False)
    sid = w["vet"].post("/api/consultations", json={"pet_id": w["pet"], "owner_id": w["owner_id"],
                                                    "veterinarian_id": vet_id}).json()["session_id"]
    assert vet.get(f"/api/vet/consultations/{sid}/workspace").status_code == 200   # reading the workspace is not a clinical act
    r = _save(vet, sid, subjective="Itching")
    assert r.status_code == 403 and r.json()["detail"]["error"] == "PRACTITIONER_AUTHORITY_REQUIRED"
    assert vet.get(f"/api/vet/consultations/{sid}/workspace").json()["soap_versions"] == 0


def test_templates_are_headings_only_in_both_languages():
    for t in soap.templates_read_model():
        assert set(t["name"]) == {"ar", "en"} and set(t["sections"]) == set(soap.SECTIONS)
        for s in soap.SECTIONS:
            for lang in ("ar", "en"):
                lines = t["sections"][s][lang].split("\n")
                assert lines and all(line.endswith(":") for line in lines), (t["template_id"], s, lang)
