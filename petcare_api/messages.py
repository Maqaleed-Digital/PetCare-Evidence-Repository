"""FR-07 — secure consultation messaging and file sharing (MVC-BUILD-RUNNER-001 U7).

AC-FR-07-01: owner and vet exchange messages and share files (images, lab reports)
within a consultation; nothing is visible outside it. AC-FR-07-02: every attempt to
deliver a notification writes a delivery record that CARRIES the rendered body
(REQ-MVC-8.67, authoritative only for delivery evidence — it does not define chat).
File bytes live in the document store (object store in production — AC-FR-07-03,
dependency PRODUCTION); only metadata and the sha256 are held here.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Protocol

from repositories import RepositoryDenied

CHANNEL_IN_APP = "IN_APP"
DELIVERED = "DELIVERED"
MAX_BODY_CHARS = 4000


@dataclass(frozen=True)
class ConsultationMessage:
    message_id: str
    tenant_id: str
    consultation_id: str
    sender_id: str
    sender_role: str
    body: str
    created_at: datetime

    def to_read_model(self) -> dict:
        d = asdict(self); d["created_at"] = self.created_at.isoformat(); return d


@dataclass(frozen=True)
class MessageAttachment:
    attachment_id: str
    message_id: str
    tenant_id: str
    filename: str
    content_type: str
    byte_size: int
    sha256: str
    storage_key: str
    created_at: datetime

    def to_read_model(self) -> dict:
        d = asdict(self); d.pop("storage_key"); d["created_at"] = self.created_at.isoformat(); return d


@dataclass(frozen=True)
class DeliveryRecord:
    record_id: str
    tenant_id: str
    message_id: str
    recipient_id: str
    channel: str
    attempt_no: int
    status: str
    rendered_body: str
    occurred_at: datetime

    def to_read_model(self) -> dict:
        d = asdict(self); d["occurred_at"] = self.occurred_at.isoformat(); return d


def validate_message(m: ConsultationMessage) -> None:
    if not m.body.strip():
        raise RepositoryDenied("a message needs a body")
    if len(m.body) > MAX_BODY_CHARS:
        raise RepositoryDenied(f"a message is at most {MAX_BODY_CHARS} characters")


class MessageRepository(Protocol):
    def add_message(self, m: ConsultationMessage) -> ConsultationMessage: ...
    def messages_for(self, consultation_id: str, *, tenant_id: str) -> list: ...
    def get_message(self, message_id: str, *, tenant_id: str): ...
    def add_attachment(self, a: MessageAttachment) -> MessageAttachment: ...
    def attachments_for(self, message_id: str, *, tenant_id: str) -> list: ...
    def record_delivery(self, r: DeliveryRecord) -> DeliveryRecord: ...
    def deliveries_for(self, message_id: str, *, tenant_id: str) -> list: ...


@dataclass
class InMemoryMessageRepository:
    tenants: object
    _messages: dict = field(default_factory=dict)
    _attachments: list = field(default_factory=list)
    _deliveries: list = field(default_factory=list)

    def add_message(self, m):
        validate_message(m)
        if self.tenants.get(m.tenant_id) is None:
            raise RepositoryDenied(f"tenant {m.tenant_id!r} is not registered")
        self._messages[m.message_id] = m
        return m

    def messages_for(self, consultation_id, *, tenant_id):
        return sorted((m for m in self._messages.values()
                       if m.consultation_id == consultation_id and m.tenant_id == tenant_id),
                      key=lambda m: (m.created_at, m.message_id))

    def get_message(self, message_id, *, tenant_id):
        m = self._messages.get(message_id)
        return m if m is not None and m.tenant_id == tenant_id else None

    def add_attachment(self, a):
        if self.get_message(a.message_id, tenant_id=a.tenant_id) is None:
            raise RepositoryDenied("attachment refers to no message in this tenant")
        self._attachments.append(a)
        return a

    def attachments_for(self, message_id, *, tenant_id):
        return [a for a in self._attachments if a.message_id == message_id and a.tenant_id == tenant_id]

    def record_delivery(self, r):
        if not r.rendered_body:
            raise RepositoryDenied("a delivery record carries the rendered body")
        self._deliveries.append(r)
        return r

    def deliveries_for(self, message_id, *, tenant_id):
        return [r for r in self._deliveries if r.message_id == message_id and r.tenant_id == tenant_id]
