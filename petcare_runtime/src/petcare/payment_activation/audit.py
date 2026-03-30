from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    event_name: str
    entity_id: str
    occurred_at: str
    actor_id: str

    def __post_init__(self) -> None:
        if not self.event_id:
            raise ValueError("event_id is required")
        if not self.event_name:
            raise ValueError("event_name is required")
        if not self.entity_id:
            raise ValueError("entity_id is required")
        if not self.occurred_at:
            raise ValueError("occurred_at is required")
        if not self.actor_id:
            raise ValueError("actor_id is required")


def authorization_event_name(target_state: str) -> str:
    return f"payment_activation.authorization.{target_state}"


def dispatch_event_name(target_state: str) -> str:
    return f"payment_activation.dispatch.{target_state}"


def safeguard_event_name(target_state: str) -> str:
    return f"payment_activation.safeguard.{target_state}"


def finalization_event_name(target_state: str) -> str:
    return f"payment_activation.finalization.{target_state}"


def build_audit_event(
    event_id: str,
    event_name: str,
    entity_id: str,
    occurred_at: str,
    actor_id: str,
) -> AuditEvent:
    return AuditEvent(
        event_id=event_id,
        event_name=event_name,
        entity_id=entity_id,
        occurred_at=occurred_at,
        actor_id=actor_id,
    )
