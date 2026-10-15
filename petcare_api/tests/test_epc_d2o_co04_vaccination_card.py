"""MVC-EPC-D-001 D2o — CO-04 vaccination card (R21.4; owner screens in ledger order). GET /api/pets/{pet_id}/vaccination-card
returns the pet's identity, the vaccinations GIVEN (a VACCINATION item with a recorded completion: title, Asia/Riyadh date, the
recording veterinarian) and the vaccinations DUE (no completion), from the FR-23 records only. A treatment is not a vaccination;
an overdue item is still due, never given. Scoped like the pet profile: another owner's or another tenant's pet is 404."""
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
import reminders as rmd  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant, grant_practitioner_authority  # noqa: E402

pytestmark = pytest.mark.served_app


def _client(user_id, tenant, role, full_name=None):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@co04.test", "pw", role, tenant_id=tenant, full_name=full_name or user_id)
    if role == "veterinarian":
        grant_practitioner_authority(user_id, tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@co04.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


@pytest.fixture()
def w():
    tag = uuid.uuid4().hex[:6]
    t = f"t-d2o-co04-{tag}"
    w = {"vet": _client(f"u-co04-vet-{tag}", t, "veterinarian", full_name="Dr Salma"),
         "owner": _client(f"u-co04-own-{tag}", t, "owner"), "other": _client(f"u-co04-oth-{tag}", t, "owner"),
         "stranger": _client(f"u-co04-str-{tag}", f"{t}-b", "owner")}
    w["pet"] = w["owner"].post("/api/pets", json={"name": "Luna", "species": "cat"}).json()["pet_id"]
    return w


def _due(vet, pet_id, title, *, in_days, kind="VACCINATION"):
    at = (datetime.now(timezone.utc) + timedelta(days=in_days)).isoformat()
    r = vet.post(f"/api/pets/{pet_id}/care-due", json={"kind": kind, "title": title, "due_at": at})
    assert r.status_code == 200, r.text
    return r.json()["due_id"]


def _card(c, pet_id):
    r = c.get(f"/api/pets/{pet_id}/vaccination-card")
    assert r.status_code == 200, r.text
    return r.json()


def test_a_completed_vaccination_is_given_with_its_veterinarian_and_an_outstanding_one_is_due(w):
    given = _due(w["vet"], w["pet"], "Rabies", in_days=-1)
    due = _due(w["vet"], w["pet"], "FVRCP booster", in_days=30)
    assert w["vet"].post(f"/api/pets/{w['pet']}/care-due/{given}/complete").status_code == 200
    card = _card(w["owner"], w["pet"])
    assert card["pet"]["name"] == "Luna" and card["pet"]["species"] == "cat"
    assert [(g["due_id"], g["title"], g["given_by"]) for g in card["given"]] == [(given, "Rabies", "Dr Salma")]
    assert card["given"][0]["given_on"] == rmd.ksa_date(datetime.now(timezone.utc)).isoformat()
    assert [(d["due_id"], d["title"]) for d in card["due"]] == [(due, "FVRCP booster")]
    assert card["issued_on"] == rmd.ksa_date(datetime.now(timezone.utc)).isoformat()


def test_an_overdue_outstanding_vaccination_is_still_due_never_given(w):
    late = _due(w["vet"], w["pet"], "Leptospirosis", in_days=-10)
    card = _card(w["owner"], w["pet"])
    assert card["given"] == []
    assert [d["due_id"] for d in card["due"]] == [late]


def test_a_treatment_is_not_a_vaccination(w):
    t = _due(w["vet"], w["pet"], "Deworming", in_days=-2, kind="TREATMENT")
    assert w["vet"].post(f"/api/pets/{w['pet']}/care-due/{t}/complete").status_code == 200
    _due(w["vet"], w["pet"], "Flea treatment", in_days=5, kind="TREATMENT")
    card = _card(w["owner"], w["pet"])
    assert card["given"] == [] and card["due"] == []


def test_another_owners_or_another_tenants_pet_card_is_not_found(w):
    _due(w["vet"], w["pet"], "Rabies", in_days=3)
    assert w["other"].get(f"/api/pets/{w['pet']}/vaccination-card").status_code == 404
    assert w["stranger"].get(f"/api/pets/{w['pet']}/vaccination-card").status_code == 404
    # the other owner's own pet card never carries this pet's items
    theirs = w["other"].post("/api/pets", json={"name": "Max", "species": "dog"}).json()["pet_id"]
    assert _card(w["other"], theirs)["due"] == []


def test_the_veterinarian_reads_the_same_card(w):
    _due(w["vet"], w["pet"], "Rabies", in_days=3)
    assert [d["title"] for d in _card(w["vet"], w["pet"])["due"]] == ["Rabies"]


def test_the_given_date_is_the_riyadh_calendar_date_of_the_recorded_completion():
    """A completion recorded at 22:30 UTC is the NEXT day in Asia/Riyadh (UTC+3)."""
    at = datetime(2031, 3, 1, 22, 30, tzinfo=timezone.utc)
    d = rmd.CareDue(due_id="d1", tenant_id="t", pet_id="p", kind=rmd.VACCINATION, title="Rabies", due_at=at,
                    recorded_by="v", created_at=at)
    c = rmd.CareCompletion(due_id="d1", tenant_id="t", completed_by="v", completed_at=at)
    card = rmd.vaccination_card([d], lambda _id: c, lambda _u: "Dr V")
    assert card["given"] == [{"due_id": "d1", "title": "Rabies", "given_on": "2031-03-02", "given_by": "Dr V"}]
    assert rmd.vaccination_card([d], lambda _id: None, lambda _u: "Dr V")["due"][0]["due_on"] == "2031-03-02"
