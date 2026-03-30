from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


CONTRACT_STATES = {
    "draft",
    "active",
    "suspended",
    "expired",
}

SLA_METRIC_TYPES = {
    "availability",
    "response_time",
    "fulfillment_time",
    "handoff_readiness",
}

BREACH_SIGNAL_STATES = {
    "none",
    "warning",
    "breach",
}


@dataclass(frozen=True)
class PartnerContract:
    contract_id: str
    partner_id: str
    tenant_id: str
    contract_state: str
    effective_from: str
    effective_to: Optional[str]
    service_scope: List[str]
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class PartnerSLA:
    sla_id: str
    contract_id: str
    metric_type: str
    target_value: int
    threshold_operator: str
    monitoring_enabled: bool
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class PartnerSLABreachSignal:
    signal_id: str
    contract_id: str
    sla_id: str
    signal_state: str
    observed_value: int
    target_value: int
    created_at: str
    notes: str


def validate_contract_state(contract_state: str) -> None:
    if contract_state not in CONTRACT_STATES:
        raise ValueError("invalid contract_state")


def validate_metric_type(metric_type: str) -> None:
    if metric_type not in SLA_METRIC_TYPES:
        raise ValueError("invalid metric_type")


def validate_signal_state(signal_state: str) -> None:
    if signal_state not in BREACH_SIGNAL_STATES:
        raise ValueError("invalid signal_state")


def validate_threshold_operator(threshold_operator: str) -> None:
    if threshold_operator not in {"lte", "gte"}:
        raise ValueError("invalid threshold_operator")
