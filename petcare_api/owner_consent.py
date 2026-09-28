"""Server-side consent ledger (MVC-EPC-D-001 Lane D, D2 — journey J-O2).

Before D2 the only consent record was a browser-local note written at registration (lib/consent.ts). This module keeps
it on the server as an APPEND-ONLY ledger: every grant and every revocation is a new event, and the current state of a
purpose is its latest event. Nothing is ever edited or deleted, so the history an owner sees is the history that
happened.

Purposes:
  privacy_notice      acknowledgement of the PDPL privacy notice, captured when the account is created. It is not
                      revocable in-app: withdrawing it means closing the account, which goes through the erasure
                      request (PDPLRightsEntry), not a toggle.
  care_reminders      care reminders about the owner's pets.
  marketing_messages  product news and offers. There is no marketing sender; the choice is recorded for when one exists.

This slice RECORDS consent. It does not yet gate reminder dispatch on `care_reminders` — coupling a recorded choice to
FR-23 delivery is a product rule not ratified here (receipt finding D2C-CONSENT-ENFORCEMENT).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

PRIVACY_NOTICE = "privacy_notice"
CARE_REMINDERS = "care_reminders"
MARKETING = "marketing_messages"
#: The DB CHECK in migration 0057 lists the same three purposes and the same two actions.
PURPOSES = (PRIVACY_NOTICE, CARE_REMINDERS, MARKETING)
REVOCABLE = frozenset({CARE_REMINDERS, MARKETING})
GRANT, REVOKE = "GRANT", "REVOKE"
ORIGINS = ("self_registration", "pilot_invite", "account_settings")
POLICY_VERSION = "privacy-notice-2026-09"


@dataclass(frozen=True)
class ConsentEvent:
    event_id: str
    tenant_id: str
    user_id: str
    purpose: str
    action: str
    origin: str
    policy_version: str
    at: datetime

    def read_model(self) -> dict:
        return {"event_id": self.event_id, "purpose": self.purpose, "action": self.action, "origin": self.origin,
                "policy_version": self.policy_version, "at": self.at.isoformat()}


def validate_event(event: ConsentEvent) -> None:
    if event.purpose not in PURPOSES or event.action not in (GRANT, REVOKE) or event.origin not in ORIGINS:
        raise ValueError("consent event is not valid")


def current_state(events: list) -> list:
    """One row per purpose, in PURPOSES order: granted or not, since when, and whether the owner may withdraw it."""
    latest: dict = {}
    for e in sorted(events, key=lambda e: (e.at, e.event_id)):
        latest[e.purpose] = e
    return [{"purpose": p, "granted": p in latest and latest[p].action == GRANT,
             "since": latest[p].at.isoformat() if p in latest else None,
             "origin": latest[p].origin if p in latest else None,
             "revocable": p in REVOCABLE} for p in PURPOSES]


@dataclass
class InMemoryOwnerConsentRepository:
    _events: list = field(default_factory=list)

    def append(self, event: ConsentEvent) -> ConsentEvent:
        validate_event(event)
        self._events.append(event)
        return event

    def events_for(self, user_id: str, *, tenant_id: str) -> list:
        return sorted((e for e in self._events if e.user_id == user_id and e.tenant_id == tenant_id),
                      key=lambda e: (e.at, e.event_id))

    def latest(self, user_id: str, purpose: str, *, tenant_id: str) -> Optional[ConsentEvent]:
        mine = [e for e in self.events_for(user_id, tenant_id=tenant_id) if e.purpose == purpose]
        return mine[-1] if mine else None
