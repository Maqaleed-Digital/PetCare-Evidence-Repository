"""MVC-EPC-D-001 D2p — CO-06 pre-visit intake with photos (R21.4). POST /api/bookings/{id}/intake: the owner of an UPCOMING
booking submits it ONCE (reason, since when, eating normally, current medications, up to 5 image photos); GET reads it back for
the owner or a veterinarian of the clinic; photos download as attachments with the exact bytes. Nothing is stored for a refused
submission; another owner's or another tenant's booking is 404."""
import os
import sys
import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bookings as bk  # noqa: E402
import main as api  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

pytestmark = pytest.mark.served_app
PNG = bytes.fromhex("89504e470d0a1a0a0000000d4948445200000001000000010806000000"
                    "1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082")
JPG = b"\xff\xd8\xff\xe0" + b"\x00" * 64 + b"\xff\xd9"


def _client(user_id, tenant, role):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@co06.test", "pw", role, tenant_id=tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@co06.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _booking(tenant, owner_id, pet_id, vet_id, *, in_hours=48, status=bk.BOOKED):
    now = datetime.now(timezone.utc)
    b = bk.Booking(booking_id=str(uuid.uuid4()), tenant_id=tenant, owner_id=owner_id, pet_id=pet_id, veterinarian_id=vet_id,
                   mode=bk.IN_CLINIC, starts_at=(now + timedelta(hours=in_hours)).replace(minute=0, second=0, microsecond=0),
                   status=status, reason="check-up", created_by_actor_id=owner_id, created_at=now, updated_at=now)
    api.BOOKING_REPO._rows[b.booking_id] = b            # direct seed: slot rules are J-O5's, not this screen's
    return b.booking_id


@pytest.fixture()
def w():
    tag = uuid.uuid4().hex[:6]
    t = f"t-d2p-co06-{tag}"
    w = {"t": t, "tag": tag, "owner": _client(f"u-co06-own-{tag}", t, "owner"), "other": _client(f"u-co06-oth-{tag}", t, "owner"),
         "vet": _client(f"u-co06-vet-{tag}", t, "veterinarian"), "admin": _client(f"u-co06-adm-{tag}", t, "partner_clinic_admin"),
         "stranger": _client(f"u-co06-str-{tag}", f"{t}-b", "veterinarian")}
    w["pet"] = w["owner"].post("/api/pets", json={"name": "Luna", "species": "cat"}).json()["pet_id"]
    w["booking"] = _booking(t, f"u-co06-own-{tag}", w["pet"], f"u-co06-vet-{tag}")
    return w


def _submit(c, booking_id, *, photos=(("a.png", PNG, "image/png"),), **fields):
    data = {"reason": "Limping on the left hind leg", "eating_normally": "YES", "symptoms_since": "",
            "current_medications": ""}
    data.update(fields)
    return c.post(f"/api/bookings/{booking_id}/intake", data=data,
                  files=[("photos", (n, b, t)) for n, b, t in photos])


def test_the_owner_submits_an_intake_with_photos_and_the_veterinarian_reads_it(w):
    since = (date.today() - timedelta(days=3)).isoformat()
    r = _submit(w["owner"], w["booking"], photos=(("leg.png", PNG, "image/png"), ("leg2.jpg", JPG, "image/jpeg")),
                symptoms_since=since, eating_normally="no", current_medications="  Meloxicam   0.5 mg ")
    assert r.status_code == 201, r.text
    body = r.json()
    assert (body["booking_id"], body["pet_id"], body["eating_normally"]) == (w["booking"], w["pet"], "NO")
    assert body["symptoms_since"] == since and body["current_medications"] == "Meloxicam 0.5 mg"
    assert [p["filename"] for p in body["photos"]] == ["leg.png", "leg2.jpg"]
    for reader in ("owner", "vet"):
        got = w[reader].get(f"/api/bookings/{w['booking']}/intake")
        assert got.status_code == 200, got.text
        assert got.json()["reason"] == "Limping on the left hind leg"
        assert len(got.json()["photos"]) == 2


def test_a_photo_downloads_as_an_attachment_with_the_exact_bytes(w):
    pid = _submit(w["owner"], w["booking"]).json()["photos"][0]["photo_id"]
    for reader in ("owner", "vet"):
        d = w[reader].get(f"/api/bookings/{w['booking']}/intake/photos/{pid}")
        assert d.status_code == 200 and d.content == PNG
        assert d.headers["content-type"] == "application/octet-stream"
        assert d.headers["content-disposition"].startswith("attachment")
    assert w["owner"].get(f"/api/bookings/{w['booking']}/intake/photos/not-a-photo").status_code == 404


def test_one_intake_per_booking_a_second_submission_is_refused_and_the_first_stands(w):
    assert _submit(w["owner"], w["booking"]).status_code == 201
    again = _submit(w["owner"], w["booking"], reason="Something else entirely")
    assert again.status_code == 409 and again.json()["detail"]["error"] == "INTAKE_ALREADY_SUBMITTED"
    assert w["owner"].get(f"/api/bookings/{w['booking']}/intake").json()["reason"] == "Limping on the left hind leg"


def test_only_an_upcoming_booked_appointment_takes_an_intake(w):
    past = _booking(w["t"], f"u-co06-own-{w['tag']}", w["pet"], f"u-co06-vet-{w['tag']}", in_hours=-2)
    cancelled = _booking(w["t"], f"u-co06-own-{w['tag']}", w["pet"], f"u-co06-vet-{w['tag']}", status=bk.CANCELLED)
    for b in (past, cancelled):
        r = _submit(w["owner"], b)
        assert r.status_code == 409 and r.json()["detail"]["error"] == "BOOKING_NOT_UPCOMING"
        assert w["owner"].get(f"/api/bookings/{b}/intake").status_code == 404


def test_photos_are_images_at_most_five_and_a_refusal_stores_nothing(w):
    pdf = _submit(w["owner"], w["booking"], photos=(("x.pdf", b"%PDF-1.4 x", "application/pdf"),))
    assert pdf.status_code == 400 and pdf.json()["detail"]["error"] == "PHOTO_NOT_IMAGE"
    six = _submit(w["owner"], w["booking"], photos=tuple((f"{i}.png", PNG, "image/png") for i in range(6)))
    assert six.status_code == 400 and six.json()["detail"]["error"] == "TOO_MANY_PHOTOS"
    empty = _submit(w["owner"], w["booking"], photos=(("e.png", b"", "image/png"),))
    assert empty.status_code == 400 and empty.json()["detail"]["error"] == "PHOTO_REJECTED"
    assert w["owner"].get(f"/api/bookings/{w['booking']}/intake").status_code == 404
    assert _submit(w["owner"], w["booking"], photos=()).status_code == 201          # photos are optional


def test_the_fields_are_validated(w):
    assert _submit(w["owner"], w["booking"], reason="   ").status_code == 400
    assert _submit(w["owner"], w["booking"], eating_normally="MAYBE").status_code == 400
    future = (date.today() + timedelta(days=5)).isoformat()
    assert _submit(w["owner"], w["booking"], symptoms_since=future).status_code == 400
    bad = _submit(w["owner"], w["booking"], symptoms_since="yesterday")
    assert bad.status_code == 400 and bad.json()["detail"]["error"] == "SYMPTOMS_SINCE_INVALID"
    assert w["owner"].get(f"/api/bookings/{w['booking']}/intake").status_code == 404


def test_another_owner_another_tenant_or_another_role_cannot_reach_it(w):
    assert _submit(w["owner"], w["booking"]).status_code == 201
    assert _submit(w["other"], w["booking"]).status_code == 404
    assert w["other"].get(f"/api/bookings/{w['booking']}/intake").status_code == 404
    assert w["stranger"].get(f"/api/bookings/{w['booking']}/intake").status_code == 404
    assert w["admin"].get(f"/api/bookings/{w['booking']}/intake").status_code == 403
    assert _submit(w["vet"], w["booking"]).status_code == 403                         # only the owner submits
