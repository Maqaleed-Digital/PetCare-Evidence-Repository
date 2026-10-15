"""MVC-EPC-D-001 D2g — X-28 (Sponsor ruling R17.4): the receipt issue date and the reminder due date shown to people are
the Asia/Riyadh calendar date. At 01:30 Riyadh the UTC date is still the previous day, so these cases discriminate; the
inputs are explicit instants, so the result is the same under TZ=UTC and TZ=Asia/Riyadh (the D2g matrix runs both)."""
import os
import sys
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import ksa_calendar  # noqa: E402
import orders  # noqa: E402
import reminders  # noqa: E402

AT_0130_RIYADH = datetime(2031, 3, 9, 22, 30, tzinfo=timezone.utc)    # 2031-03-10 01:30 Riyadh; UTC date 2031-03-09
AT_1200_RIYADH = datetime(2031, 3, 10, 9, 0, tzinfo=timezone.utc)
ORDER = SimpleNamespace(order_id="o-1", lines=(SimpleNamespace(product_id="P", quantity=1, unit_price_halalas=1000),))
COLL = SimpleNamespace(amount_halalas=1000, reference="REF-1")


@pytest.mark.parametrize("at", [AT_0130_RIYADH, AT_1200_RIYADH], ids=["0130-riyadh", "1200-riyadh"])
def test_the_receipt_issue_date_is_the_riyadh_date(at):
    assert "Issued: 2031-03-10" in orders.render_receipt(ORDER, COLL, "en", at)
    assert "تاريخ الإصدار: 2031-03-10" in orders.render_receipt(ORDER, COLL, "ar", at)


@pytest.mark.parametrize("at", [AT_0130_RIYADH, AT_1200_RIYADH], ids=["0130-riyadh", "1200-riyadh"])
def test_the_reminder_due_date_is_the_riyadh_date(at):
    item = SimpleNamespace(due_at=at, kind=reminders.VACCINATION, title="Rabies")
    assert "2031-03-10" in reminders.render(item, reminders.REMIND_24H, "en", "Luna")
    assert "2031-03-10" in reminders.render(item, reminders.REMIND_24H, "ar", "لونا")
    assert "2031-03-09" not in reminders.render(item, reminders.REMIND_24H, "en", "Luna")


def test_the_ksa_calendar_is_asia_riyadh_and_refuses_a_naive_instant():
    assert str(ksa_calendar.KSA_ZONE) == "Asia/Riyadh"
    assert ksa_calendar.ksa_date(AT_0130_RIYADH).isoformat() == "2031-03-10"
    with pytest.raises(ValueError):
        ksa_calendar.ksa_date(datetime(2031, 3, 10, 1, 30))
