from __future__ import annotations

from dataclasses import dataclass

from .authorization import AuthorizationRecord
from .dispatch import DispatchRecord
from .finalization import FinalizationRecord
from .treasury import TreasuryCheckRecord


@dataclass(frozen=True)
class ControlledExecutionCase:
    execution_id: str
    authorization: AuthorizationRecord
    treasury_check: TreasuryCheckRecord | None = None
    dispatch: DispatchRecord | None = None
    finalization: FinalizationRecord | None = None


def create_controlled_execution_case(
    execution_id: str,
    authorization: AuthorizationRecord,
) -> ControlledExecutionCase:
    return ControlledExecutionCase(
        execution_id=execution_id,
        authorization=authorization,
    )


def attach_treasury_check(
    case: ControlledExecutionCase,
    treasury_check: TreasuryCheckRecord,
) -> ControlledExecutionCase:
    return ControlledExecutionCase(
        execution_id=case.execution_id,
        authorization=case.authorization,
        treasury_check=treasury_check,
        dispatch=case.dispatch,
        finalization=case.finalization,
    )


def attach_dispatch(
    case: ControlledExecutionCase,
    dispatch: DispatchRecord,
) -> ControlledExecutionCase:
    return ControlledExecutionCase(
        execution_id=case.execution_id,
        authorization=case.authorization,
        treasury_check=case.treasury_check,
        dispatch=dispatch,
        finalization=case.finalization,
    )


def attach_finalization(
    case: ControlledExecutionCase,
    finalization: FinalizationRecord,
) -> ControlledExecutionCase:
    return ControlledExecutionCase(
        execution_id=case.execution_id,
        authorization=case.authorization,
        treasury_check=case.treasury_check,
        dispatch=case.dispatch,
        finalization=finalization,
    )
