from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from petcare.partner_network.contracts_repository import PartnerContractsRepository
from petcare.partner_network.contracts_service import (
    create_contract,
    define_sla,
    record_breach_signal,
    transition_contract_state,
)
from petcare.partner_network.contracts_query import (
    get_active_contracts,
    get_contract_breach_signals,
    get_contract_slas,
)

router = APIRouter(tags=["ep07-wave02"])

repo = PartnerContractsRepository()


class ContractCreateRequest(BaseModel):
    contract_id: str
    partner_id: str
    tenant_id: str
    effective_from: str
    effective_to: Optional[str] = None
    service_scope: List[str]


class ContractStateRequest(BaseModel):
    contract_id: str
    new_state: str


class SLADefineRequest(BaseModel):
    sla_id: str
    contract_id: str
    metric_type: str
    target_value: int
    threshold_operator: str
    monitoring_enabled: bool = True


class BreachSignalRequest(BaseModel):
    signal_id: str
    contract_id: str
    sla_id: str
    signal_state: str
    observed_value: int
    notes: str


@router.post("/ep07/contracts/create")
def create_contract_api(payload: ContractCreateRequest):
    contract = create_contract(
        repo=repo,
        contract_id=payload.contract_id,
        partner_id=payload.partner_id,
        tenant_id=payload.tenant_id,
        effective_from=payload.effective_from,
        effective_to=payload.effective_to,
        service_scope=payload.service_scope,
    )
    return contract.__dict__


@router.post("/ep07/contracts/state")
def update_contract_state_api(payload: ContractStateRequest):
    contract = transition_contract_state(
        repo=repo,
        contract_id=payload.contract_id,
        new_state=payload.new_state,
    )
    return contract.__dict__


@router.post("/ep07/contracts/sla")
def define_sla_api(payload: SLADefineRequest):
    sla = define_sla(
        repo=repo,
        sla_id=payload.sla_id,
        contract_id=payload.contract_id,
        metric_type=payload.metric_type,
        target_value=payload.target_value,
        threshold_operator=payload.threshold_operator,
        monitoring_enabled=payload.monitoring_enabled,
    )
    return sla.__dict__


@router.post("/ep07/contracts/breach-signal")
def record_breach_signal_api(payload: BreachSignalRequest):
    signal = record_breach_signal(
        repo=repo,
        signal_id=payload.signal_id,
        contract_id=payload.contract_id,
        sla_id=payload.sla_id,
        signal_state=payload.signal_state,
        observed_value=payload.observed_value,
        notes=payload.notes,
    )
    return signal.__dict__


@router.get("/ep07/contracts/active")
def list_active_contracts():
    return [item.__dict__ for item in get_active_contracts(repo)]


@router.get("/ep07/contracts/{contract_id}/slas")
def list_contract_slas(contract_id: str):
    return [item.__dict__ for item in get_contract_slas(repo, contract_id)]


@router.get("/ep07/contracts/{contract_id}/signals")
def list_contract_signals(contract_id: str):
    return [item.__dict__ for item in get_contract_breach_signals(repo, contract_id)]
