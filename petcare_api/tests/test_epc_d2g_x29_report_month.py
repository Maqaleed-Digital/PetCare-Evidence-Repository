"""MVC-EPC-D-001 D2g — X-29 (Sponsor ruling R18.1): the regulated antimicrobial report buckets a prescription in the
Asia/Riyadh calendar month of its issue. Between 00:00 and 02:59 Riyadh on the 1st of a month the UTC instant is still in
the previous month, so a UTC bucket is wrong exactly there.
  - test_the_report_month_now_is_the_riyadh_month: issued at the CURRENT clock (the D2g month matrix pins it per cell);
  - test_the_month_boundary: fixed instants around 1 March 2031 Riyadh (served clock pinned).
"""
import os
import sys
import uuid
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
from test_fr30_compliance import _client, _issue, _register  # noqa: E402

pytestmark = pytest.mark.served_app
RIYADH = ZoneInfo("Asia/Riyadh")
BOUNDARY = {                                                   # instant -> regulated (Riyadh) report month
    "last-day-2359": (datetime(2031, 2, 28, 20, 59, tzinfo=timezone.utc), "2031-02"),
    "first-0000": (datetime(2031, 2, 28, 21, 0, tzinfo=timezone.utc), "2031-03"),
    "first-0130": (datetime(2031, 2, 28, 22, 30, tzinfo=timezone.utc), "2031-03"),
    "first-0259": (datetime(2031, 2, 28, 23, 59, tzinfo=timezone.utc), "2031-03"),
    "first-0300": (datetime(2031, 3, 1, 0, 0, tzinfo=timezone.utc), "2031-03"),
}


def _world():
    tag = uuid.uuid4().hex[:6]
    t = f"t-d2g-x29-{tag}"
    vet = _client(f"u-x29-vet-{tag}", t, "veterinarian")
    owner = _client(f"u-x29-owner-{tag}", t, "owner")
    admin = _client(f"u-x29-admin-{tag}", t, "partner_clinic_admin")
    _register("amoxi-x29", agent="amoxicillin", agent_class="penicillin")
    pet = owner.post("/api/pets", json={"name": "Cat", "species": "cat"}).json()["pet_id"]
    return vet, admin, pet


def _period_of(admin, rx_id):
    rows = [r for r in admin.get("/api/compliance/antimicrobials").json()["rows"] if rx_id in r["prescription_ids"]]
    assert len(rows) == 1, rows
    return rows[0]["period"]


def test_the_report_month_now_is_the_riyadh_month():
    vet, admin, pet = _world()
    rx = _issue(vet, pet, "amoxi-x29")
    want = datetime.now(RIYADH).strftime("%Y-%m")
    got = _period_of(admin, rx)
    assert got == want, f"regulated report month {got!r} != Asia/Riyadh month {want!r}"


@pytest.mark.parametrize("cell", list(BOUNDARY))
def test_the_month_boundary(monkeypatch, cell):
    vet, admin, pet = _world()
    instant, want = BOUNDARY[cell]
    real = datetime

    class _Pinned(real):
        @classmethod
        def now(cls, tz=None):
            return instant.astimezone(tz) if tz is not None else instant.astimezone().replace(tzinfo=None)

    monkeypatch.setattr(api, "datetime", _Pinned)
    rx = _issue(vet, pet, "amoxi-x29")
    got = _period_of(admin, rx)
    assert got == want, f"regulated report month {got!r} != Asia/Riyadh month {want!r} at {instant.isoformat()}"
