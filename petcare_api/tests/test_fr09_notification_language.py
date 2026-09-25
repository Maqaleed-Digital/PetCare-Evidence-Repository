"""FR-09 AC-FR-09-03 — notifications and generated documents are produced in the RECIPIENT's chosen language
(MVC-BUILD-RUNNER-001 U19). Every notification/document the served app produces is covered: consultation-message
notifications (FR-07), recall notices (FR-19), COD receipts (FR-20) and care reminders (FR-23)."""
import os
import re
import sys
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
from inventory import REGISTRATION_SOURCE, ProductRegistration  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant, grant_practitioner_authority, stock_origin  # noqa: E402

pytestmark = pytest.mark.served_app
T = "t-fr09-notify"
ARABIC = re.compile(r"[؀-ۿ]")


def _client(user_id, role):
    ensure_tenant(T)
    auth.seed_user(user_id, f"{user_id}@fr09n.test", "pw", role, tenant_id=T)
    if role == "veterinarian":
        grant_practitioner_authority(user_id, T)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@fr09n.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _general(product):
    if product not in api.INVENTORY_REPO._products:
        api.INVENTORY_REPO.register_product(ProductRegistration(product_id=product, name=product, supply_class="GENERAL",
                                                                source=REGISTRATION_SOURCE,
                                                                registered_at=datetime.now(timezone.utc)))


def _documents_for(owner_id, owner, vet, admin):
    """Drive every notification/document path for one owner; return {kind: text}."""
    pet = owner.post("/api/pets", json={"name": "Luna", "species": "cat"}).json()["pet_id"]
    out = {}
    # FR-07 message notification
    sess = vet.post("/api/consultations", json={"pet_id": pet, "owner_id": owner_id,
                                                "veterinarian_id": vet.get("/api/auth/me").json()["user_id"]}).json()
    msg = vet.post(f"/api/consultations/{sess['session_id']}/messages", json={"body": "lab results ready"}).json()
    (rec,) = api.MESSAGE_REPO.deliveries_for(msg["message_id"], tenant_id=T)
    assert rec.recipient_id == owner_id
    out["message_notification"] = rec.rendered_body
    # FR-19 recall notice
    rx = vet.post("/api/prescriptions", json={"pet_id": pet, "session_id": "s", "medication_name": "m", "dosage": "d",
                                              "instructions": "i"}).json()["prescription_id"]
    vet.post(f"/api/prescriptions/{rx}/verify")
    batch = f"LOT-{owner_id}"
    assert vet.post(f"/api/prescriptions/{rx}/dispense",
                    json=stock_origin(T, product_id="vax-09n", batch=batch)).status_code == 200
    admin.post("/api/recalls", json={"product_id": "vax-09n", "batch": batch, "reason": "potency"})
    out["recall_notice"] = [n["body"] for n in owner.get("/api/me/recall-notices").json() if batch in n["body"]][0]
    # FR-23 reminder
    due = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    vet.post(f"/api/pets/{pet}/care-due", json={"kind": "VACCINATION", "title": "Rabies", "due_at": due})
    admin.post("/api/reminders/run")
    out["reminder"] = owner.get("/api/me/reminders").json()[-1]["body"]
    # FR-20 receipt
    _general("brush-09n")
    admin.post("/api/catalog/prices", json={"product_id": "brush-09n", "unit_price_halalas": 1500})
    loc = admin.post("/api/inventory/locations", json={"name": f"Shop {owner_id}"}).json()["location_id"]
    admin.post("/api/inventory/movements", json={"location_id": loc, "product_id": "brush-09n", "batch": "S",
                                                 "quantity_delta": 5, "reason": "RECEIPT", "batch_expiry": "2030-01-01"})
    o = owner.post("/api/orders", json={"lines": [{"product_id": "brush-09n", "quantity": 1}], "payment_method": "COD"}).json()
    admin.post(f"/api/orders/{o['order_id']}/deliver", json={"location_id": loc, "batches": {"brush-09n": "S"},
                                                            "collected_amount_halalas": 1500, "collection_reference": "C"})
    out["receipt"] = owner.get(f"/api/orders/{o['order_id']}/receipt").json()["rendered"]
    return out


def test_every_notification_and_document_is_in_the_recipients_language():
    vet = _client("u-fr09n-vet", "veterinarian")
    admin = _client("u-fr09n-admin", "partner_clinic_admin")
    owner_ar = _client("u-fr09n-owner-ar", "owner")                     # no preference: Arabic (primary)
    owner_en = _client("u-fr09n-owner-en", "owner")
    assert owner_en.put("/api/me/preferences/language", json={"language": "en"}).status_code == 200
    ar = _documents_for("u-fr09n-owner-ar", owner_ar, vet, admin)
    en = _documents_for("u-fr09n-owner-en", owner_en, vet, admin)
    assert set(ar) == set(en) == {"message_notification", "recall_notice", "reminder", "receipt"}
    for kind, text in ar.items():
        assert ARABIC.search(text), f"Arabic-preferring owner got an English-only {kind}: {text!r}"
    for kind, text in en.items():
        assert not ARABIC.search(text), f"English-preferring owner got Arabic in {kind}: {text!r}"
