from __future__ import annotations

from typing import List

from petcare.partner_network.contracts import PartnerContract, PartnerSLA, PartnerSLABreachSignal
from petcare.partner_network.contracts_repository import PartnerContractsRepository


def get_active_contracts(repo: PartnerContractsRepository) -> List[PartnerContract]:
    return sorted(
        [item for item in repo.list_contracts() if item.contract_state == "active"],
        key=lambda item: item.contract_id,
    )


def get_contract_slas(repo: PartnerContractsRepository, contract_id: str) -> List[PartnerSLA]:
    return repo.list_slas_by_contract(contract_id)


def get_contract_breach_signals(repo: PartnerContractsRepository, contract_id: str) -> List[PartnerSLABreachSignal]:
    return repo.list_signals_by_contract(contract_id)
