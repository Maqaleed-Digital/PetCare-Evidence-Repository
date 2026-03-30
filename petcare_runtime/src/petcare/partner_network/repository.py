from __future__ import annotations

from typing import Dict, List

from petcare.partner_network.models import Partner


class PartnerRepository:
    def __init__(self) -> None:
        self._store: Dict[str, Partner] = {}

    def add(self, partner: Partner) -> None:
        self._store[partner.partner_id] = partner

    def get(self, partner_id: str) -> Partner:
        return self._store[partner_id]

    def list_all(self) -> List[Partner]:
        return sorted(self._store.values(), key=lambda p: p.partner_id)

    def list_by_state(self, state: str) -> List[Partner]:
        return sorted(
            [p for p in self._store.values() if p.verification_state == state],
            key=lambda p: p.partner_id,
        )
