"""FR-14 prescription upload and vet verification — ratified AC-FR-14-01..07 through the SERVED
app (MVC-BUILD-RUNNER-001 U9). Every test drives main:app with signed sessions.

AC-FR-14-06 (EXTERNAL:SFDA_API) and AC-FR-14-07 (PRODUCTION) are exercised only as far as is
internally buildable — the port's contract and the measuring instrument. Neither dependency is
evidenced here and none is claimed.
"""
import os
import sys
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
import sfda  # noqa: E402
from inventory import REGISTRATION_SOURCE, ProductRegistration  # noqa: E402
from practitioners import CLASS_VETERINARIAN, PractitionerAuthorityGrant  # noqa: E402
from prescriptions import Prescription  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant, grant_practitioner_authority, stock_origin  # noqa: E402

pytestmark = pytest.mark.served_app
T_A, T_B = "t-rx14-alpha", "t-rx14-beta"
RX = {"pet_id": "pet-1", "session_id": "sess-1", "medication_name": "Amoxicillin", "dosage": "50mg",
      "instructions": "bid"}
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


def _client(user_id, tenant, role, *, authority=True):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@rx14.test", "pw", role, tenant_id=tenant)
    if role == "veterinarian" and authority:
        grant_practitioner_authority(user_id, tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@rx14.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _events(c, name=None):
    ev = c.get("/audit/events/tenant", params={"limit": 5000}).json()["events"]
    return [e for e in ev if name is None or e["event_name"] == name]


def _issue(vet):
    r = vet.post("/api/prescriptions", json=RX)
    assert r.status_code == 200, r.text
    return r.json()["prescription_id"]


def _register(product_id, klass):
    if api.INVENTORY_REPO.supply_class_of(product_id) != klass:
        api.INVENTORY_REPO.register_product(ProductRegistration(
            product_id=product_id, name=product_id, supply_class=klass, source=REGISTRATION_SOURCE,
            registered_at=datetime.now(timezone.utc)))


def _stocked_location(admin, vet, product, qty=10):
    loc = admin.post("/api/inventory/locations", json={"name": f"Rx {product} {uuid4().hex[:6]}"}).json()["location_id"]
    who = vet if api.INVENTORY_REPO.supply_class_of(product) in ("POM", "RESTRICTED", "CONTROLLED") else admin
    r = who.post("/api/inventory/movements", json={"location_id": loc, "product_id": product, "batch": "L1",
                                                   "quantity_delta": qty, "reason": "RECEIPT",
                                                   "batch_expiry": "2099-12-31"})
    assert r.status_code == 200, r.text
    return loc


# --------------------------------------------------------------------------- AC-FR-14-01
def test_issue_upload_verify_dispense_only_through_the_governed_transitions():
    vet = _client("u-rx14-vet-1", T_A, "veterinarian")
    rx = _issue(vet)  # no tenant in the body: the session decides
    assert vet.post(f"/api/prescriptions/{rx}/documents",
                    files={"file": ("rx.png", PNG, "image/png")}).status_code == 200
    assert rx in [p["prescription_id"] for p in vet.get("/api/prescriptions/queue/awaiting-verification").json()]
    assert vet.post(f"/api/prescriptions/{rx}/dispense").status_code == 409  # not verified yet
    assert vet.post(f"/api/prescriptions/{rx}/verify").status_code == 200
    assert vet.post(f"/api/prescriptions/{rx}/verify").status_code == 409  # outside the governed set
    assert vet.post(f"/api/prescriptions/{rx}/dispense", json=stock_origin(T_A)).status_code == 200
    assert vet.post(f"/api/prescriptions/{rx}/dispense", json=stock_origin(T_A)).status_code == 409
    moves = [(t["from_status"], t["to_status"]) for t in vet.get(f"/api/prescriptions/{rx}/transitions").json()]
    assert moves[-2:] == [("ISSUED", "VET_VERIFIED"), ("VET_VERIFIED", "DISPENSED")]
    assert vet.get(f"/api/prescriptions/{rx}").json()["status"] == "DISPENSED"
    # A body naming another tenant is refused, not honoured.
    assert vet.post("/api/prescriptions", json={**RX, "tenant_id": T_B}).status_code == 403


# --------------------------------------------------------------------------- AC-FR-14-02
def test_dispensing_never_authorises_on_a_client_asserted_class():
    vet = _client("u-rx14-vet-2", T_A, "veterinarian")
    admin = _client("u-rx14-admin-2", T_A, "partner_clinic_admin")
    rx = _issue(vet)
    assert vet.post(f"/api/prescriptions/{rx}/verify").status_code == 200
    r = admin.post(f"/api/prescriptions/{rx}/dispense", headers={"X-Supply-Class": "GENERAL",
                                                                  "X-Professional-Class": "PHARMACIST"})
    assert r.status_code == 403
    denied = [e for e in _events(admin, "prescription.dispense_denied") if e["resource_id"] == rx]
    assert denied and denied[-1]["actor_id"] == "u-rx14-admin-2" and denied[-1]["action_result"] == "denied"
    assert vet.get(f"/api/prescriptions/{rx}").json()["status"] == "VET_VERIFIED"
    # The supply path takes no class from the client at all.
    _register("amoxi-14", "POM")
    loc = _stocked_location(admin, vet, "amoxi-14")
    body = {"location_id": loc, "product_id": "amoxi-14", "batch": "L1", "quantity": 1, "prescription_id": rx}
    assert admin.post("/api/inventory/supplies", json={**body, "supply_class": "GENERAL"}).status_code == 422
    assert admin.post("/api/inventory/supplies", json=body).status_code == 403
    assert vet.get(f"/api/prescriptions/{rx}").json()["status"] == "VET_VERIFIED"


# --------------------------------------------------------------------------- AC-FR-14-03
@pytest.mark.parametrize("klass", ["GENERAL", "OTC"])
def test_general_and_otc_are_supplied_without_a_prescription(klass):
    admin = _client("u-rx14-admin-3", T_A, "partner_clinic_admin")
    vet = _client("u-rx14-vet-3", T_A, "veterinarian")
    product = f"item-{klass.lower()}-14"
    _register(product, klass)
    loc = _stocked_location(admin, vet, product)
    r = admin.post("/api/inventory/supplies", json={"location_id": loc, "product_id": product, "batch": "L1",
                                                    "quantity": 3})
    assert r.status_code == 200, r.text
    assert r.json()["prescription_required"] is False and r.json()["reason"] == "SUPPLY"
    stock = admin.get("/api/inventory/stock", params={"product_id": product}).json()["locations"]
    assert [b["quantity"] for x in stock if x["location_id"] == loc for b in x["stock"]] == [7]


@pytest.mark.parametrize("product,klass", [("pom-14", "POM"), ("res-14", "RESTRICTED"),
                                           ("ctl-14", "CONTROLLED"), ("unreg-14", None)])
def test_pom_restricted_controlled_are_never_supplied_without_a_verified_prescription(product, klass):
    admin = _client("u-rx14-admin-4", T_A, "partner_clinic_admin")
    vet = _client("u-rx14-vet-4", T_A, "veterinarian")
    if klass:
        _register(product, klass)
    loc = _stocked_location(admin, vet, product)
    body = {"location_id": loc, "product_id": product, "batch": "L1", "quantity": 2}
    r = vet.post("/api/inventory/supplies", json=body)
    assert r.status_code == 403 and r.json()["detail"]["error"] == "PRESCRIPTION_REQUIRED"
    unverified = _issue(vet)
    assert vet.post("/api/inventory/supplies", json={**body, "prescription_id": unverified}).status_code == 409
    assert vet.post(f"/api/prescriptions/{unverified}/verify").status_code == 200
    ok = vet.post("/api/inventory/supplies", json={**body, "prescription_id": unverified})
    assert ok.status_code == 200, ok.text
    assert ok.json()["prescription_required"] is True and ok.json()["prescription_id"] == unverified
    assert vet.get(f"/api/prescriptions/{unverified}").json()["status"] == "DISPENSED"
    # A dispensed prescription cannot be supplied against again.
    assert vet.post("/api/inventory/supplies", json={**body, "prescription_id": unverified}).status_code == 409
    refused = [e for e in _events(vet, "inventory.supply.refused") if e["resource_id"] == product]
    assert {e["reason_code"] for e in refused} >= {"PRESCRIPTION_REQUIRED", "PRESCRIPTION_NOT_VERIFIED"}


# --------------------------------------------------------------------------- AC-FR-14-04
def test_a_vet_without_a_live_authority_is_refused_naming_the_attribute_and_its_expiry():
    vet = _client("u-rx14-vet-lapsed", T_A, "veterinarian", authority=False)
    past = datetime.now(timezone.utc) - timedelta(days=3)
    expires = past + timedelta(days=1)
    api.PERSISTENCE.practitioners.grant(PractitionerAuthorityGrant(
        grant_id=str(uuid4()), tenant_id=T_A, actor_id="u-rx14-vet-lapsed", professional_class=CLASS_VETERINARIAN,
        licence_ref="LIC-EXPIRED", effective_from=past, expires_at=expires, granted_by_actor_id="test-fixture",
        granted_at=past))
    status = vet.get("/api/practitioners/me/authority").json()
    assert status["in_force"] is False and status["reason"].startswith("expired at")
    before = len(vet.get("/api/prescriptions/queue/awaiting-verification").json())
    r = vet.post("/api/prescriptions", json=RX)
    assert r.status_code == 403
    detail = r.json()["detail"]
    assert detail["attribute"] == CLASS_VETERINARIAN
    assert detail["reason"] == f"expired at {expires.isoformat()}"
    assert len(vet.get("/api/prescriptions/queue/awaiting-verification").json()) == before  # nothing signed


# --------------------------------------------------------------------------- AC-FR-14-05
def test_every_prescription_read_and_transition_is_tenant_scoped_and_audited():
    vet = _client("u-rx14-vet-5", T_A, "veterinarian")
    other = _client("u-rx14-vet-5b", T_B, "veterinarian")
    rx = _issue(vet)
    vet.post(f"/api/prescriptions/{rx}/documents", files={"file": ("rx.png", PNG, "image/png")})
    assert vet.post(f"/api/prescriptions/{rx}/verify").status_code == 200
    for path in (f"/api/prescriptions/{rx}", f"/api/prescriptions/{rx}/documents",
                 f"/api/prescriptions/{rx}/transitions"):
        assert vet.get(path).status_code == 200
        assert other.get(path).status_code == 404
    assert other.post(f"/api/prescriptions/{rx}/verify").status_code == 404
    assert other.post(f"/api/prescriptions/{rx}/sfda-validation").status_code == 404
    assert rx not in [p["prescription_id"] for p in other.get("/api/prescriptions/queue/awaiting-dispense").json()]
    mine = [e for e in _events(vet) if e["resource_id"] == rx]
    names = {e["event_name"] for e in mine}
    assert {"prescription.issued", "prescription.vet_verified", "prescription.viewed",
            "prescription.documents_listed", "prescription.transitions_viewed"} <= names
    assert all(e["actor_id"] == "u-rx14-vet-5" and e["tenant_id"] == T_A for e in mine)
    assert not [e for e in _events(other) if e["resource_id"] == rx]


# --------------------------------------------------------------------------- AC-FR-14-06 (port contract only)
class _ContractDouble:
    """Stands in for the SFDA interface per the port contract. NOT an integration."""
    answers = {}

    def validate(self, *, prescription_id, medication_name):
        a = self.answers.get(prescription_id)
        if a == "RAISE":
            raise TimeoutError("interface did not answer")
        return a if a is not None else sfda.SfdaResult(sfda.UNKNOWN, "SFDA does not know this prescription")


def test_the_sfda_port_never_treats_an_invalid_or_unknown_prescription_as_valid(monkeypatch):
    vet = _client("u-rx14-vet-6", T_A, "veterinarian")
    served = vet.post(f"/api/prescriptions/{_issue(vet)}/sfda-validation").json()  # as deployed: no adapter
    assert (served["status"], served["valid"]) == ("UNAVAILABLE", False)
    double = _ContractDouble()
    monkeypatch.setattr(api, "SFDA_PORT", double)
    ids = {k: _issue(vet) for k in ("valid", "invalid", "unknown", "raise", "junk")}
    double.answers = {ids["valid"]: sfda.SfdaResult(sfda.VALID), ids["invalid"]: sfda.SfdaResult(sfda.INVALID),
                      ids["raise"]: "RAISE", ids["junk"]: "yes"}
    got = {k: vet.post(f"/api/prescriptions/{v}/sfda-validation").json() for k, v in ids.items()}
    assert {k: (g["status"], g["valid"]) for k, g in got.items()} == {
        "valid": ("VALID", True), "invalid": ("INVALID", False), "unknown": ("UNKNOWN", False),
        "raise": ("UNAVAILABLE", False), "junk": ("UNKNOWN", False)}
    audited = {e["resource_id"]: e["reason_code"] for e in _events(vet, "prescription.sfda_validated")}
    assert audited[ids["invalid"]] == "SFDA_INVALID" and audited[ids["valid"]] == "SFDA_VALID"


# --------------------------------------------------------------------------- AC-FR-14-07 (instrument only)
def test_the_verification_time_instrument_reports_the_share_within_thirty_minutes():
    tenant = "t-rx14-metric"
    vet = _client("u-rx14-vet-7", tenant, "veterinarian")
    now = datetime.now(timezone.utc)
    for i in range(20):
        issued = now - timedelta(minutes=45 if i < 2 else 5)  # 2 of 20 late = 10% > 5%
        rid = str(uuid4())
        api.PRESCRIPTION_REPO.create(Prescription(
            prescription_id=rid, tenant_id=tenant, pet_id="p", session_id="s", issuing_vet_id="u-rx14-vet-7",
            medication_name="m", dosage="d", instructions="i", status="ISSUED", issued_at=issued),
            actor_id="u-rx14-vet-7", actor_role="veterinarian")
        assert vet.post(f"/api/prescriptions/{rid}/verify").status_code == 200
    m = vet.get("/api/prescriptions/metrics/verification-time").json()
    assert (m["verified"], m["within_target"], m["target_minutes"]) == (20, 18, 30)
    assert m["share_within_target"] == 0.9 and m["meets_target"] is False and m["p95_minutes"] > 30
