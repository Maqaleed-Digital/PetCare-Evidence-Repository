from __future__ import annotations

from typing import Dict, List

from petcare.partner_network.contracts import (
    PartnerContract,
    PartnerSLA,
    PartnerSLABreachSignal,
)


class PartnerContractsRepository:
    def __init__(self) -> None:
        self._contracts: Dict[str, PartnerContract] = {}
        self._slas: Dict[str, PartnerSLA] = {}
        self._signals: Dict[str, PartnerSLABreachSignal] = {}

    def add_contract(self, contract: PartnerContract) -> None:
        self._contracts[contract.contract_id] = contract

    def get_contract(self, contract_id: str) -> PartnerContract:
        return self._contracts[contract_id]

    def list_contracts(self) -> List[PartnerContract]:
        return sorted(self._contracts.values(), key=lambda item: item.contract_id)

    def list_contracts_by_partner(self, partner_id: str) -> List[PartnerContract]:
        return sorted(
            [item for item in self._contracts.values() if item.partner_id == partner_id],
            key=lambda item: item.contract_id,
        )

    def add_sla(self, sla: PartnerSLA) -> None:
        self._slas[sla.sla_id] = sla

    def get_sla(self, sla_id: str) -> PartnerSLA:
        return self._slas[sla_id]

    def list_slas_by_contract(self, contract_id: str) -> List[PartnerSLA]:
        return sorted(
            [item for item in self._slas.values() if item.contract_id == contract_id],
            key=lambda item: item.sla_id,
        )

    def add_signal(self, signal: PartnerSLABreachSignal) -> None:
        self._signals[signal.signal_id] = signal

    def list_signals_by_contract(self, contract_id: str) -> List[PartnerSLABreachSignal]:
        return sorted(
            [item for item in self._signals.values() if item.contract_id == contract_id],
            key=lambda item: item.signal_id,
        )
