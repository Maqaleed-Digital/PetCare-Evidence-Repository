"""MVC-EPC-D-001 D2f — X-22, Sponsor ruling R16.3 (Option B): Saudi veterinary licence validity is judged on the
Asia/Riyadh calendar date, explicitly, whatever the host machine's zone and whatever the UTC calendar says.

Every case pins the instant the SERVED registration route reads (`routers.auth.datetime`) to one point near a calendar
boundary, so these tests mean the same thing under TZ=UTC, TZ=Asia/Riyadh or TZ=Asia/Dubai. The discriminating
instants are the two where the Riyadh date and the UTC date differ (00:00–03:00 Riyadh); a UTC-calendar rule gives the
opposite answer there.
"""
import os
import sys
import uuid
from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import licences  # noqa: E402
import main as api  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

pytestmark = pytest.mark.served_app
T = "t-d2f-x22"
PW = "Pw-long-enough-1"

AT_0130 = datetime(2031, 3, 9, 22, 30, tzinfo=timezone.utc)   # 2031-03-10 01:30 Riyadh — Riyadh and UTC dates differ
AT_0030 = datetime(2031, 3, 9, 21, 30, tzinfo=timezone.utc)   # 2031-03-10 00:30 Riyadh — dates differ
AT_1200 = datetime(2031, 3, 10, 9, 0, tzinfo=timezone.utc)    # 2031-03-10 12:00 Riyadh — dates agree
AT_2330 = datetime(2031, 3, 10, 20, 30, tzinfo=timezone.utc)  # 2031-03-10 23:30 Riyadh — dates agree


def _pin(monkeypatch, instant):
    real = datetime

    class _Pinned(real):
        @classmethod
        def now(cls, tz=None):
            return instant.astimezone(tz) if tz is not None else instant.astimezone().replace(tzinfo=None)

    monkeypatch.setattr(auth, "datetime", _Pinned)


def _register(expires_on):
    ensure_tenant(T)
    code = f"D2F-{uuid.uuid4().hex[:8]}"
    auth.seed_invite_code(code, "veterinarian")
    body = {"email": f"vet-{uuid.uuid4().hex[:8]}@d2f.test", "password": PW, "invite_code": code,
            "role": "veterinarian", "name": "Dr Calendar",
            "licence": {"licence_number": f"MEWA-{uuid.uuid4().hex[:6]}", "issuing_authority": "MEWA",
                        "expires_on": expires_on}}
    return TestClient(api.app).post("/api/auth/register", json=body)


def _error(r):
    return r.json()["detail"]["error"] if r.status_code == 400 else r.status_code


@pytest.mark.parametrize("instant", [AT_0130, AT_0030], ids=["0130-riyadh", "0030-riyadh"])
def test_a_licence_that_expired_yesterday_in_riyadh_is_refused_though_it_is_still_today_in_utc(monkeypatch, instant):
    _pin(monkeypatch, instant)
    assert _error(_register("2031-03-09")) == "LICENCE_EXPIRED"     # the UTC date is 2031-03-09: a UTC rule admits it


@pytest.mark.parametrize("instant", [AT_0130, AT_0030, AT_1200, AT_2330],
                         ids=["0130-riyadh", "0030-riyadh", "1200-riyadh", "2330-riyadh"])
def test_a_licence_valid_through_today_in_riyadh_registers(monkeypatch, instant):
    _pin(monkeypatch, instant)
    r = _register("2031-03-10")
    assert r.status_code == 201, r.text


@pytest.mark.parametrize("instant", [AT_1200, AT_2330], ids=["1200-riyadh", "2330-riyadh"])
def test_a_licence_that_expired_yesterday_is_refused_when_the_calendars_agree(monkeypatch, instant):
    _pin(monkeypatch, instant)
    assert _error(_register("2031-03-09")) == "LICENCE_EXPIRED"


def test_the_licence_calendar_is_asia_riyadh_and_refuses_a_naive_instant():
    assert str(licences.LICENCE_CALENDAR_ZONE) == "Asia/Riyadh"
    assert licences.licence_calendar_date(AT_0130) == date(2031, 3, 10) != AT_0130.date()
    assert licences.licence_calendar_date(AT_2330) == date(2031, 3, 10) == AT_2330.date()
    with pytest.raises(ValueError):
        licences.licence_calendar_date(datetime(2031, 3, 10, 1, 30))


def test_the_repository_judges_submission_on_the_riyadh_calendar():
    repo = licences.InMemoryLicenceRepository()

    def lic(expires_on, at):
        return licences.VetLicence(licence_id=str(uuid.uuid4()), actor_id="u-v", licence_number="MEWA-1",
                                   issuing_authority="MEWA", expires_on=expires_on, submitted_at=at)

    with pytest.raises(licences.RepositoryDenied):
        repo.submit(lic(date(2031, 3, 9), AT_0130))                  # Riyadh 10 Mar; UTC 9 Mar
    assert repo.submit(lic(date(2031, 3, 10), AT_0130)).expires_on == date(2031, 3, 10)
