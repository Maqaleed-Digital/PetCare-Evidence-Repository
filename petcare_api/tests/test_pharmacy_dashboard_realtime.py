"""AC-FR-27-01 — the dispensing dashboard shows a new verified prescription within the ratified
bound: REAL_TIME_BOUND = 5 s, p95 over at least 100 events (MVC-BUILD-RUNNER-001 U6).

Measured through the SERVED app. For each of 100 events a veterinarian verifies a
prescription and a SECOND authorised dashboard session reads the queue until the item is
visible. The dashboard's end-to-end latency is bounded by server visibility latency plus
the UI refresh interval (petcare_web/lib/pharmacyQueue.ts), so the assertion is
    p95(server visibility latency) + QUEUE_REFRESH_MS <= 5 s.
Another tenant's dashboard must never show any of these items.
"""
import os
import re
import sys
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant, grant_practitioner_authority  # noqa: E402

pytestmark = pytest.mark.served_app
T_A, T_B = "t-dash-alpha", "t-dash-beta"
EVENTS = 100
BOUND_S = 5.0
REFRESH = Path(__file__).resolve().parents[2] / "petcare_web" / "lib" / "pharmacyQueue.ts"


def _refresh_seconds() -> float:
    m = re.search(r"QUEUE_REFRESH_MS\s*=\s*(\d+)", REFRESH.read_text(encoding="utf-8"))
    assert m, "QUEUE_REFRESH_MS not found"
    return int(m.group(1)) / 1000.0


def _client(user_id: str, tenant: str, role: str) -> TestClient:
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@dash.test", "pw", role, tenant_id=tenant)
    if role == "veterinarian":
        grant_practitioner_authority(user_id, tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@dash.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _p95(samples: list) -> float:
    s = sorted(samples)
    return s[max(0, int(round(0.95 * len(s))) - 1)]


def test_new_verified_prescription_visible_within_bound_p95_over_100_events():
    vet = _client("u-dash-vet", T_A, "veterinarian")
    dashboard = _client("u-dash-clinic", T_A, "partner_clinic_admin")
    other_tenant = _client("u-dash-vet-b", T_B, "veterinarian")
    latencies, ids = [], []
    for i in range(EVENTS):
        rx = vet.post("/api/prescriptions", json={
            "pet_id": f"p{i}", "session_id": "s", "tenant_id": T_A, "medication_name": "amoxicillin",
            "dosage": "50mg", "instructions": "bid"}).json()
        assert vet.post(f"/api/prescriptions/{rx['prescription_id']}/verify").status_code == 200
        committed = time.perf_counter()
        deadline = committed + BOUND_S
        while True:
            queue = dashboard.get("/api/prescriptions/queue/awaiting-dispense").json()
            if any(q["prescription_id"] == rx["prescription_id"] for q in queue):
                latencies.append(time.perf_counter() - committed)
                break
            assert time.perf_counter() < deadline, f"event {i} not visible within {BOUND_S}s"
        ids.append(rx["prescription_id"])
    assert len(latencies) >= 100
    p95 = _p95(latencies)
    worst_case = p95 + _refresh_seconds()
    assert worst_case <= BOUND_S, (p95, _refresh_seconds())
    foreign = other_tenant.get("/api/prescriptions/queue/awaiting-dispense").json()
    assert not {q["prescription_id"] for q in foreign} & set(ids)
