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

D2d (Sponsor ruling R10 / X-25): `care_reminders` is ENFORCED at the FR-23 dispatch boundary, not only recorded.
`reminder_dispatch_decision` is read from this server ledger immediately before each send and fails closed: absent,
revoked, malformed or unreadable consent means no dispatch. The ledger has no expiry semantics, so none is applied.
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


#: Why a reminder was not dispatched. Every value except CONSENT_GRANTED refuses.
CONSENT_GRANTED, CONSENT_ABSENT, CONSENT_REVOKED = "CONSENT_GRANTED", "CONSENT_ABSENT", "CONSENT_REVOKED"
CONSENT_MALFORMED, CONSENT_UNREADABLE = "CONSENT_MALFORMED", "CONSENT_UNREADABLE"


def reminder_dispatch_decision(repo, owner_id: str, *, tenant_id: str) -> tuple:
    """(admitted, reason) for one FR-23 reminder to `owner_id` in `tenant_id`, from the server ledger only.

    Fails closed: admitted only when the owner's latest `care_reminders` event in THIS tenant is a well-formed GRANT.
    A read error, a record that is not a ConsentEvent for this owner/tenant/purpose, or an unknown action refuses."""
    try:
        latest = repo.latest(owner_id, CARE_REMINDERS, tenant_id=tenant_id)
    except Exception:  # noqa: BLE001 — any failure to read the ledger is indeterminate consent, never permission
        return False, CONSENT_UNREADABLE
    if latest is None:
        return False, CONSENT_ABSENT
    if (not isinstance(latest, ConsentEvent) or latest.user_id != owner_id or latest.tenant_id != tenant_id
            or latest.purpose != CARE_REMINDERS or latest.action not in (GRANT, REVOKE)):
        return False, CONSENT_MALFORMED
    if latest.action == REVOKE:
        return False, CONSENT_REVOKED
    return True, CONSENT_GRANTED


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
