"""MVC-EPC-D-001 D2g — J-O7 (FR-14 owner part): an owner sees the prescriptions issued for their own pets and uploads a
prescription written elsewhere for verification. Owner, tenant and pets come from the session; the request only selects
one of the owner's own pets and carries the file. Another owner's pets, prescriptions and uploads are invisible (404)."""
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
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


def _client(user_id, tenant, role):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@d2g-jo7.test", "pw", role, full_name=user_id, tenant_id=tenant)
    if role == "veterinarian":
        grant_practitioner_authority(user_id, tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@d2g-jo7.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


@pytest.fixture()
def w():
    tag = uuid.uuid4().hex[:6]
    t, other = f"t-d2g-jo7-{tag}", f"t-d2g-jo7-o-{tag}"
    w = {"owner": _client(f"u-o-{tag}", t, "owner"), "owner2": _client(f"u-o2-{tag}", t, "owner"),
         "vet": _client(f"u-v-{tag}", t, "veterinarian"), "foreign_vet": _client(f"u-fv-{tag}", other, "veterinarian"),
         "owner_id": f"u-o-{tag}"}
    w["pet"] = w["owner"].post("/api/pets", json={"name": "Luna", "species": "cat"}).json()["pet_id"]
    w["pet2"] = w["owner2"].post("/api/pets", json={"name": "Max", "species": "dog"}).json()["pet_id"]
    return w


def _upload(c, pet, data=PNG, ctype="image/png", note="from the previous clinic"):
    return c.post("/api/owner/prescriptions/uploads", data={"pet_id": pet, "note": note},
                  files={"file": ("rx.png", data, ctype)})


def test_an_owner_sees_the_prescriptions_issued_for_their_own_pets(w):
    rx = {"pet_id": w["pet"], "session_id": "s1", "medication_name": "Amoxicillin", "dosage": "50mg", "instructions": "bid"}
    mine = w["vet"].post("/api/prescriptions", json=rx)
    assert mine.status_code == 200, mine.text
    other = w["vet"].post("/api/prescriptions", json={**rx, "pet_id": w["pet2"]})
    assert other.status_code == 200
    body = w["owner"].get("/api/owner/prescriptions").json()
    assert [p["prescription_id"] for p in body["prescriptions"]] == [mine.json()["prescription_id"]]
    assert body["prescriptions"][0]["medication_name"] == "Amoxicillin"


def test_an_owner_uploads_an_external_prescription_for_verification(w):
    r = _upload(w["owner"], w["pet"])
    assert r.status_code == 201, r.text
    u = r.json()
    assert (u["status"], u["pet_id"], u["owner_id"]) == ("AWAITING_VERIFICATION", w["pet"], w["owner_id"])
    assert "storage_key" not in u
    assert [x["upload_id"] for x in w["owner"].get("/api/owner/prescriptions").json()["uploads"]] == [u["upload_id"]]
    doc = w["owner"].get(f"/api/owner/prescriptions/uploads/{u['upload_id']}/document")
    assert doc.status_code == 200 and doc.content == PNG
    assert doc.headers["content-type"].startswith("application/octet-stream")   # never rendered inline
    queue = w["vet"].get("/api/prescriptions/uploads/awaiting-verification").json()
    assert [x["upload_id"] for x in queue] == [u["upload_id"]]
    assert w["foreign_vet"].get("/api/prescriptions/uploads/awaiting-verification").json() == []


def test_an_owner_cannot_upload_for_or_see_another_owners_pet(w):
    assert _upload(w["owner"], w["pet2"]).status_code == 404
    assert _upload(w["owner"], "no-such-pet").status_code == 404
    u = _upload(w["owner2"], w["pet2"]).json()
    assert w["owner"].get(f"/api/owner/prescriptions/uploads/{u['upload_id']}/document").status_code == 404
    assert w["owner"].get("/api/owner/prescriptions").json()["uploads"] == []


def test_an_unsupported_or_empty_file_is_refused_and_nothing_is_recorded(w):
    assert _upload(w["owner"], w["pet"], data=b"<script>", ctype="text/html").status_code == 400
    assert _upload(w["owner"], w["pet"], data=b"", ctype="image/png").status_code == 400
    assert w["owner"].get("/api/owner/prescriptions").json()["uploads"] == []


def test_the_routes_are_owner_only_and_the_queue_is_veterinarian_only(w):
    assert w["vet"].get("/api/owner/prescriptions").status_code == 403
    assert _upload(w["vet"], w["pet"]).status_code == 403
    assert w["owner"].get("/api/prescriptions/uploads/awaiting-verification").status_code == 403


def test_every_upload_is_audited(w):
    u = _upload(w["owner"], w["pet"]).json()
    ev = w["owner"].get("/audit/events/tenant", params={"limit": 5000})
    if ev.status_code == 200:
        assert any(e["event_name"] == "prescription.owner_uploaded" and e["resource_id"] == u["upload_id"]
                   for e in ev.json()["events"])
    else:
        vet_ev = w["vet"].get("/audit/events/tenant", params={"limit": 5000}).json()["events"]
        assert any(e["event_name"] == "prescription.owner_uploaded" and e["resource_id"] == u["upload_id"] for e in vet_ev)
