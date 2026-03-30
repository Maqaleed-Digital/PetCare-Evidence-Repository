from __future__ import annotations

from .models import ApprovalRecord, ExecutionInstruction, ExecutionRecord


def execute_instruction(
    instruction: ExecutionInstruction,
    execution_id: str,
    executed_by: str,
    executed_at: str,
    execution_approval: ApprovalRecord,
) -> ExecutionRecord:
    if not execution_approval.approval_id:
        raise ValueError("execution approval is required")

    return ExecutionRecord(
        execution_id=execution_id,
        instruction_id=instruction.instruction_id,
        executed_by=executed_by,
        executed_at=executed_at,
        execution_approval_id=execution_approval.approval_id,
    )
