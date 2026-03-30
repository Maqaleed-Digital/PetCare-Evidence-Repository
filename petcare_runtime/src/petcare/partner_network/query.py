from __future__ import annotations

from typing import List

from petcare.partner_network.repository import PartnerRepository
from petcare.partner_network.models import Partner


def get_verified_partners(repo: PartnerRepository) -> List[Partner]:
    return repo.list_by_state("verified")


def get_pending_partners(repo: PartnerRepository) -> List[Partner]:
    return sorted(
        [
            p
            for p in repo.list_all()
            if p.verification_state in {"submitted", "under_review"}
        ],
        key=lambda p: p.partner_id,
    )
