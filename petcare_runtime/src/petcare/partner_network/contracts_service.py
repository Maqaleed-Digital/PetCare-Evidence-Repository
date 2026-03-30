from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from petcare.partner_network.contracts import (
    PartnerContract,
    PartnerSLA,
    PartnerSLABreachSignal,
    validate_contract_state,
    validate_metric_type,
    validate_signal_state,
    validate_threshold_operator,
)
from petcare.partner_network.contracts_repository import PartnerContractsRepository


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def create_contract(
    repo: PartnerContractsRepository,
    contract_id: str,
    partner_id: str,
    tenant_id: str,
    effective_from: str,
    effective_to: Optional[str],
    service_scope: List[str],
) -> PartnerContract:
    contract = PartnerContract(
        contract_id=contract_id,
        partner_id=partner_id,
        tenant_id=tenant_id,
        contract_state="draft",
        effective_from=effective_from,
        effective_to=effective_to,
        service_scope=list(service_scope),
        created_at=_now(),
        updated_at=_now(),
    )
    repo.add_contract(contract)
    return contract


def transition_contract_state(
    repo: PartnerContractsRepository,
    contract_id: str,
    new_state: str,
) -> PartnerContract:
    validate_contract_state(new_state)

    current = repo.get_contract(contract_id)
    updated = PartnerContract(
        contract_id=current.contract_id,
        partner_id=current.partner_id,
        tenant_id=current.tenant_id,
        contract_state=new_state,
        effective_from=current.effective_from,
        effective_to=current.effective_to,
        service_scope=list(current.service_scope),
        created_at=current.created_at,
        updated_at=_now(),
    )
    repo.add_contract(updated)
    return updated


def define_sla(
    repo: PartnerContractsRepository,
    sla_id: str,
    contract_id: str,
    metric_type: str,
    target_value: int,
    threshold_operator: str,
    monitoring_enabled: bool = True,
) -> PartnerSLA:
    validate_metric_type(metric_type)
    validate_threshold_operator(threshold_operator)

    _ = repo.get_contract(contract_id)

    sla = PartnerSLA(
        sla_id=sla_id,
        contract_id=contract_id,
        metric_type=metric_type,
        target_value=int(target_value),
        threshold_operator=threshold_operator,
        monitoring_enabled=bool(monitoring_enabled),
        created_at=_now(),
        updated_at=_now(),
    )
    repo.add_sla(sla)
    return sla


def record_breach_signal(
    repo: PartnerContractsRepository,
    signal_id: str,
    contract_id: str,
    sla_id: str,
    signal_state: str,
    observed_value: int,
    notes: str,
) -> PartnerSLABreachSignal:
    validate_signal_state(signal_state)

    contract = repo.get_contract(contract_id)
    sla = repo.get_sla(sla_id)

    if sla.contract_id != contract.contract_id:
        raise ValueError("sla_contract_mismatch")

    signal = PartnerSLABreachSignal(
        signal_id=signal_id,
        contract_id=contract_id,
        sla_id=sla_id,
        signal_state=signal_state,
        observed_value=int(observed_value),
        target_value=int(sla.target_value),
        created_at=_now(),
        notes=notes,
    )
    repo.add_signal(signal)
    return signal
