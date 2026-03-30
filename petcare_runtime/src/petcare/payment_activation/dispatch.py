from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .authorization import AuthorizationRecord, AuthorizationStatus
from .treasury import TreasuryCheckRecord, TreasuryStatus


class RailType(str, Enum):
    BANK_API = "bank_api"
    GATEWAY_API = "gateway_api"
    PAYOUT_PROVIDER = "payout_provider"


class DispatchStatus(str, Enum):
    DISPATCHED = "dispatched"
    DISPATCH_BLOCKED = "dispatch_blocked"
    ACKNOWLEDGED = "acknowledged"


@dataclass(frozen=True)
class RailConnectorContract:
    connector_id: str
    rail_type: RailType
    governed_mode: str
    contract_version: str

    def __post_init__(self) -> None:
        if not self.connector_id:
            raise ValueError("connector_id is required")
        if self.governed_mode != "governed_dispatch_only":
            raise ValueError("connector must remain governed_dispatch_only")
        if not self.contract_version:
            raise ValueError("contract_version is required")


@dataclass(frozen=True)
class DispatchRecord:
    dispatch_id: str
    execution_id: str
    connector_id: str
    status: DispatchStatus
    dispatched_at: str
    dispatched_by: str
    acknowledgement_ref: str | None = None

    def __post_init__(self) -> None:
        if not self.dispatch_id:
            raise ValueError("dispatch_id is required")
        if not self.execution_id:
            raise ValueError("execution_id is required")
        if not self.connector_id:
            raise ValueError("connector_id is required")
        if not self.dispatched_at:
            raise ValueError("dispatched_at is required")
        if not self.dispatched_by:
            raise ValueError("dispatched_by is required")


def build_rail_connector_contract(
    connector_id: str,
    rail_type: RailType,
    contract_version: str,
) -> RailConnectorContract:
    return RailConnectorContract(
        connector_id=connector_id,
        rail_type=rail_type,
        governed_mode="governed_dispatch_only",
        contract_version=contract_version,
    )


def dispatch_execution(
    dispatch_id: str,
    execution_id: str,
    connector: RailConnectorContract,
    authorization: AuthorizationRecord,
    treasury_check: TreasuryCheckRecord,
    dispatched_at: str,
    dispatched_by: str,
) -> DispatchRecord:
    authorized_ok = authorization.status in {
        AuthorizationStatus.AUTHORIZED,
        AuthorizationStatus.DUAL_AUTHORIZED,
    }
    treasury_ok = treasury_check.status == TreasuryStatus.SUFFICIENT

    if not authorized_ok or not treasury_ok:
        return DispatchRecord(
            dispatch_id=dispatch_id,
            execution_id=execution_id,
            connector_id=connector.connector_id,
            status=DispatchStatus.DISPATCH_BLOCKED,
            dispatched_at=dispatched_at,
            dispatched_by=dispatched_by,
        )

    return DispatchRecord(
        dispatch_id=dispatch_id,
        execution_id=execution_id,
        connector_id=connector.connector_id,
        status=DispatchStatus.DISPATCHED,
        dispatched_at=dispatched_at,
        dispatched_by=dispatched_by,
    )
