"""X-30 precondition fixture (MVC-EPC-D-001 D2h; Sponsor rulings R18.2 + R18.3).

Delivery now refuses unless the supplying location holds a licence valid today (Asia/Riyadh). Frozen tests that deliver get a
licence for their location as ENTITY DATA (R18.2 — a licence the product validates, not a regulatory determination), recorded
through the governed path: a platform administrator of the location's own tenant posts it to the served
POST /api/admin/establishment-licences, so the product's own validation runs. No assertion of any frozen test changes.
"""
import os
import sys
import uuid

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import main as api  # noqa: E402
from routers import auth  # noqa: E402


def licensed_location(staff: TestClient, location_id: str, expires_on: str = "2099-12-31") -> dict:
    """Record a licence for `location_id` in the tenant of the signed-in `staff` client; return the recorded licence."""
    tenant = auth.IDENTITY_REPO.get_by_user_id(staff.get("/api/auth/me").json()["user_id"]).tenant_id
    admin_id = f"u-estlic-{uuid.uuid4().hex[:8]}"
    auth.seed_user(admin_id, f"{admin_id}@estlic.test", "pw", "platform_admin", tenant_id=tenant)
    admin = TestClient(api.app)
    r = admin.post("/api/auth/sign-in", json={"email": f"{admin_id}@estlic.test", "password": "pw"})
    if r.status_code != 200:
        raise AssertionError(f"precondition: platform admin sign-in failed: {r.status_code}")
    admin.cookies.set("petcare_session", r.cookies["petcare_session"])
    lic = admin.post("/api/admin/establishment-licences", json={
        "location_id": location_id, "licence_number": f"SFDA-EST-{uuid.uuid4().hex[:6]}", "issuing_authority": "SFDA",
        "expires_on": expires_on, "basis": "test entity data (R18.2): licence certificate fixture",
        "licence_type": "PHARMACY_ESTABLISHMENT", "scope": "veterinary medicines supply (test entity data)",
        "evidence_document_ref": f"DOC-TEST-{uuid.uuid4().hex[:6]}"})     # R19.2 fields (D2k)
    if lic.status_code != 201:
        raise AssertionError(f"precondition: governed establishment-licence record failed: {lic.status_code} {lic.text}")
    return lic.json()
