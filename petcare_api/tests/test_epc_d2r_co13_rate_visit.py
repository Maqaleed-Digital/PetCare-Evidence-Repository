"""MVC-EPC-D-001 D2r — CO-13 rate visit (R21.4). The owner rates their OWN COMPLETED consultation once (1..5, optional comment);
the rating is insert-only; the consultation's veterinarian and the clinic administrator read it; another owner, another
veterinarian and another tenant cannot rate or read it."""
import os
import sys
import uuid

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant, grant_practitioner_authority  # noqa: E402

pytestmark = pytest.mark.served_app


def _client(user_id, tenant, role):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@co13.test", "pw", role, full_name=user_id, tenant_id=tenant)
    if role == "veterinarian":
        grant_practitioner_authority(user_id, tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@co13.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


@pytest.fixture()
def w():
    tag = uuid.uuid4().hex[:6]
    t = f"t-d2r-co13-{tag}"
    w = {"owner_id": f"u-r-own-{tag}", "vet_id": f"u-r-vet-{tag}"}
    w["owner"] = _client(w["owner_id"], t, "owner")
    w["other"] = _client(f"u-r-oth-{tag}", t, "owner")
    w["vet"] = _client(w["vet_id"], t, "veterinarian")
    w["vet2"] = _client(f"u-r-vet2-{tag}", t, "veterinarian")
    w["admin"] = _client(f"u-r-adm-{tag}", t, "partner_clinic_admin")
    w["stranger"] = _client(f"u-r-str-{tag}", f"{t}-b", "owner")
    w["pet"] = w["owner"].post("/api/pets", json={"name": "Luna", "species": "cat"}).json()["pet_id"]
    return w


def _visit(w, *, complete=True):
    r = w["vet"].post("/api/consultations", json={"pet_id": w["pet"], "owner_id": w["owner_id"], "veterinarian_id": w["vet_id"]})
    assert r.status_code == 200, r.text
    sid = r.json()["session_id"]
    if complete:
        assert w["vet"].post(f"/api/consultations/{sid}/outcome", json={"outcome": "Healthy"}).status_code == 200
    return sid


def _rate(c, sid, **body):
    return c.post(f"/api/owner/consultations/{sid}/rating", json={"score": 5, "comment": "  Very   kind vet ", **body})


def test_the_owner_rates_a_completed_visit_once_and_reads_it_back(w):
    sid = _visit(w)
    r = _rate(w["owner"], sid)
    assert r.status_code == 201, r.text
    assert (r.json()["score"], r.json()["comment"]) == (5, "Very kind vet")
    again = _rate(w["owner"], sid, score=1, comment="changed")
    assert again.status_code == 409 and again.json()["detail"]["error"] == "VISIT_ALREADY_RATED"
    got = w["owner"].get(f"/api/owner/consultations/{sid}/rating").json()
    assert (got["score"], got["comment"]) == (5, "Very kind vet")


def test_an_incomplete_visit_cannot_be_rated(w):
    sid = _visit(w, complete=False)
    r = _rate(w["owner"], sid)
    assert r.status_code == 409 and r.json()["detail"]["error"] == "VISIT_NOT_COMPLETED"
    assert w["owner"].get(f"/api/owner/consultations/{sid}/rating").status_code == 404


@pytest.mark.parametrize("score", [0, 6, -1, 2.5, True, "five"])
def test_the_score_is_a_whole_number_from_1_to_5(w, score):
    sid = _visit(w)
    assert _rate(w["owner"], sid, score=score).status_code in (400, 422)
    assert w["owner"].get(f"/api/owner/consultations/{sid}/rating").status_code == 404


def test_a_long_comment_is_refused(w):
    sid = _visit(w)
    assert _rate(w["owner"], sid, comment="x" * 501).status_code == 400
    assert _rate(w["owner"], sid, comment="").status_code == 201                 # the comment is optional


def test_only_the_owner_rates_and_only_the_owners_vet_or_clinic_admin_reads(w):
    sid = _visit(w)
    assert _rate(w["other"], sid).status_code == 404
    assert _rate(w["stranger"], sid).status_code == 404
    assert _rate(w["vet"], sid).status_code == 403
    assert _rate(w["owner"], sid, score=4).status_code == 201
    assert w["vet"].get(f"/api/consultations/{sid}/rating").json()["score"] == 4
    assert w["admin"].get(f"/api/consultations/{sid}/rating").json()["score"] == 4
    assert w["vet2"].get(f"/api/consultations/{sid}/rating").status_code == 403
    assert w["other"].get(f"/api/owner/consultations/{sid}/rating").status_code == 404
    assert w["other"].get(f"/api/consultations/{sid}/rating").status_code == 403
