from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExternalSignalTrust(str, Enum):
    UNTRUSTED = "untrusted"
    REVIEW_REQUIRED = "review_required"
    PASSIVE_ACCEPTED = "passive_accepted"


@dataclass(frozen=True)
class ExternalSignalRecord:
    signal_id: str
    source_system: str
    payload_ref: str
    received_at: str
    trust_status: ExternalSignalTrust
    requires_human_review: bool

    def __post_init__(self) -> None:
        if not self.signal_id:
            raise ValueError("signal_id is required")
        if not self.source_system:
            raise ValueError("source_system is required")
        if not self.payload_ref:
            raise ValueError("payload_ref is required")
        if not self.received_at:
            raise ValueError("received_at is required")


def build_signal_record(
    signal_id: str,
    source_system: str,
    payload_ref: str,
    received_at: str,
    trust_status: ExternalSignalTrust,
) -> ExternalSignalRecord:
    return ExternalSignalRecord(
        signal_id=signal_id,
        source_system=source_system,
        payload_ref=payload_ref,
        received_at=received_at,
        trust_status=trust_status,
        requires_human_review=trust_status != ExternalSignalTrust.PASSIVE_ACCEPTED,
    )


def validate_signal_for_review(signal: ExternalSignalRecord) -> bool:
    return signal.requires_human_review
