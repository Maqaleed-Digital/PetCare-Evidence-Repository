"""KSA calendar for dates shown to people (MVC-EPC-D-001 D2g, X-28 / Sponsor ruling R17.4).

A receipt's issue date and a reminder's due date are the Asia/Riyadh calendar date of the instant — the same basis as the
licence-validity rule (licences.LICENCE_CALENDAR_ZONE, X-22) — never the UTC date and never the host's.
"""
from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

KSA_ZONE = ZoneInfo("Asia/Riyadh")


def ksa_date(at: datetime) -> date:
    """The Asia/Riyadh calendar date of an instant. A naive instant is refused rather than guessed."""
    if at.tzinfo is None or at.utcoffset() is None:
        raise ValueError("a KSA calendar date needs a timezone-aware instant")
    return at.astimezone(KSA_ZONE).date()
