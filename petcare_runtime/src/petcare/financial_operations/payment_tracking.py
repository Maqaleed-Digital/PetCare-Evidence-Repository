from __future__ import annotations

from .models import PaymentStatusRecord, PaymentTrackingStatus


_ALLOWED_TRANSITIONS: dict[PaymentTrackingStatus, set[PaymentTrackingStatus]] = {
    PaymentTrackingStatus.PENDING_EXTERNAL: {PaymentTrackingStatus.RECEIVED_EXTERNAL_SIGNAL, PaymentTrackingStatus.UNDER_REVIEW},
    PaymentTrackingStatus.RECEIVED_EXTERNAL_SIGNAL: {PaymentTrackingStatus.UNDER_REVIEW},
    PaymentTrackingStatus.UNDER_REVIEW: {PaymentTrackingStatus.MATCHED, PaymentTrackingStatus.MISMATCHED},
    PaymentTrackingStatus.MATCHED: {PaymentTrackingStatus.CLOSED},
    PaymentTrackingStatus.MISMATCHED: {PaymentTrackingStatus.UNDER_REVIEW, PaymentTrackingStatus.CLOSED},
    PaymentTrackingStatus.CLOSED: set(),
}


def start_payment_tracking(
    instruction_id: str,
    started_at: str,
    external_reference_id: str | None = None,
) -> PaymentStatusRecord:
    return PaymentStatusRecord(
        instruction_id=instruction_id,
        external_reference_id=external_reference_id,
        status=PaymentTrackingStatus.PENDING_EXTERNAL,
        last_updated_at=started_at,
    )


def record_external_signal(
    record: PaymentStatusRecord,
    signaled_at: str,
    signal_source: str,
    payload_ref: str,
) -> PaymentStatusRecord:
    if record.status not in {PaymentTrackingStatus.PENDING_EXTERNAL, PaymentTrackingStatus.UNDER_REVIEW}:
        raise ValueError("external signal cannot be recorded from current state")
    return PaymentStatusRecord(
        instruction_id=record.instruction_id,
        external_reference_id=record.external_reference_id,
        status=PaymentTrackingStatus.RECEIVED_EXTERNAL_SIGNAL,
        last_updated_at=signaled_at,
        last_signal_source=signal_source,
        last_signal_payload_ref=payload_ref,
    )


def transition_payment_tracking(
    record: PaymentStatusRecord,
    target_status: PaymentTrackingStatus,
    transitioned_at: str,
) -> PaymentStatusRecord:
    if target_status not in _ALLOWED_TRANSITIONS[record.status]:
        raise ValueError(f"invalid payment tracking transition: {record.status.value} -> {target_status.value}")
    return PaymentStatusRecord(
        instruction_id=record.instruction_id,
        external_reference_id=record.external_reference_id,
        status=target_status,
        last_updated_at=transitioned_at,
        last_signal_source=record.last_signal_source,
        last_signal_payload_ref=record.last_signal_payload_ref,
    )
