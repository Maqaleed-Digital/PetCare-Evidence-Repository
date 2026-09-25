"""FR-23 — vaccination and treatment reminders (MVC-BUILD-RUNNER-001 U15).

AC-FR-23-01 (ratified): REMINDER_DEFAULT = 7 days before due; SECOND_REMINDER = 24 hours before due IF
OUTSTANDING. Configuration may add reminders but may not suppress these defaults — there is no
suppression path at all. A recorded due date produces the reminders to the pet's owner of the SAME
tenant, never another tenant's.
AC-FR-23-02: reminders are rendered in the owner's chosen language (Arabic primary) and each send is
audited. Sends are idempotent: one reminder per (due item, kind).
AC-FR-23-03/04 (EXTERNAL:SMS_GATEWAY): delivery here is IN_APP; the SMS gateway is not integrated.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Protocol

from repositories import RepositoryDenied

VACCINATION, TREATMENT = "VACCINATION", "TREATMENT"
KINDS = (VACCINATION, TREATMENT)
REMIND_7D, REMIND_24H = "REMIND_7D", "REMIND_24H"
DEFAULT_OFFSETS = {REMIND_7D: timedelta(days=7), REMIND_24H: timedelta(hours=24)}
CHANNEL_IN_APP = "IN_APP"


@dataclass(frozen=True)
class CareDue:
    due_id: str
    tenant_id: str
    pet_id: str
    kind: str
    title: str
    due_at: datetime
    recorded_by: str
    created_at: datetime


@dataclass(frozen=True)
class CareCompletion:
    due_id: str
    tenant_id: str
    completed_by: str
    completed_at: datetime


@dataclass(frozen=True)
class Reminder:
    reminder_id: str
    due_id: str
    tenant_id: str
    owner_id: str
    kind: str
    language: str
    rendered: str
    channel: str
    sent_at: datetime


def reminders_due(item: CareDue, *, now: datetime, completed: bool, already: set) -> list:
    """The reminder kinds to send for `item` at `now`. 7-day: once inside 7 days of due (until due).
    24-hour: once inside 24 hours of due, only while outstanding. Never suppressible."""
    out = []
    if item.due_at <= now:
        return out
    if now >= item.due_at - DEFAULT_OFFSETS[REMIND_7D] and REMIND_7D not in already:
        out.append(REMIND_7D)
    if not completed and now >= item.due_at - DEFAULT_OFFSETS[REMIND_24H] and REMIND_24H not in already:
        out.append(REMIND_24H)
    return out


def render(item: CareDue, kind: str, language: str, pet_name: str) -> str:
    when = item.due_at.date().isoformat()
    if language == "ar":
        what = "تطعيم" if item.kind == VACCINATION else "علاج"
        lead = "تذكير: خلال ٢٤ ساعة" if kind == REMIND_24H else "تذكير: خلال ٧ أيام"
        return f"{lead} — موعد {what} «{item.title}» لحيوانك {pet_name} بتاريخ {when}."
    what = "vaccination" if item.kind == VACCINATION else "treatment"
    lead = "Reminder: within 24 hours" if kind == REMIND_24H else "Reminder: within 7 days"
    return f"{lead} — {pet_name}'s {what} \"{item.title}\" is due on {when}."


def validate_due(d: CareDue) -> None:
    if d.kind not in KINDS:
        raise RepositoryDenied(f"kind must be one of {KINDS}")
    if not d.title.strip() or len(d.title) > 200:
        raise RepositoryDenied("a due item has a title of 1..200 characters")
    if d.due_at.tzinfo is None:
        raise RepositoryDenied("a due date carries its offset")


class ReminderRepository(Protocol):
    def add_due(self, d: CareDue) -> CareDue: ...
    def get_due(self, due_id: str, *, tenant_id: str): ...
    def dues(self, *, tenant_id: str) -> list: ...
    def complete(self, c: CareCompletion) -> CareCompletion: ...
    def completed(self, due_id: str, *, tenant_id: str) -> bool: ...
    def record(self, r: Reminder) -> bool: ...
    def sent_kinds(self, due_id: str, *, tenant_id: str) -> set: ...
    def for_owner(self, owner_id: str, *, tenant_id: str) -> list: ...


@dataclass
class InMemoryReminderRepository:
    tenants: object
    _dues: dict = field(default_factory=dict)
    _done: dict = field(default_factory=dict)
    _sent: list = field(default_factory=list)

    def add_due(self, d):
        validate_due(d)
        if self.tenants.get(d.tenant_id) is None:
            raise RepositoryDenied(f"tenant {d.tenant_id!r} is not registered")
        self._dues[d.due_id] = d
        return d

    def get_due(self, due_id, *, tenant_id):
        d = self._dues.get(due_id)
        return d if d is not None and d.tenant_id == tenant_id else None

    def dues(self, *, tenant_id):
        return sorted((d for d in self._dues.values() if d.tenant_id == tenant_id), key=lambda d: (d.due_at, d.due_id))

    def complete(self, c):
        if self.get_due(c.due_id, tenant_id=c.tenant_id) is None:
            raise RepositoryDenied("completion refers to no due item in this tenant")
        if c.due_id in self._done:
            raise RepositoryDenied("already completed")
        self._done[c.due_id] = c
        return c

    def completed(self, due_id, *, tenant_id):
        c = self._done.get(due_id)
        return c is not None and c.tenant_id == tenant_id

    def record(self, r):
        """Idempotent: False when this (due item, kind) was already sent."""
        if any(x.due_id == r.due_id and x.kind == r.kind for x in self._sent):
            return False
        self._sent.append(r)
        return True

    def sent_kinds(self, due_id, *, tenant_id):
        return {x.kind for x in self._sent if x.due_id == due_id and x.tenant_id == tenant_id}

    def for_owner(self, owner_id, *, tenant_id):
        return sorted((x for x in self._sent if x.owner_id == owner_id and x.tenant_id == tenant_id),
                      key=lambda x: (x.sent_at, x.reminder_id))
