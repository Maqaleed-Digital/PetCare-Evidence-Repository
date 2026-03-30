from __future__ import annotations

from .models import ExecutionInstruction


def export_instruction_payload(instruction: ExecutionInstruction) -> dict[str, str]:
    return {
        "instruction_id": instruction.instruction_id,
        "settlement_id": instruction.settlement_id,
        "payment_method": instruction.payment_method.value,
        "currency": instruction.currency,
        "gross_total": str(instruction.gross_total),
        "platform_fee_total": str(instruction.platform_fee_total),
        "net_payout_total": str(instruction.net_payout_total),
        "created_by": instruction.created_by,
        "created_at": instruction.created_at,
        "settlement_approval_id": instruction.settlement_approval_id,
        "payload_checksum": instruction.payload_checksum,
        "execution_mode": "non_autonomous_export_only",
    }
