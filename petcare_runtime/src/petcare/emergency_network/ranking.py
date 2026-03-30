from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple


CAPACITY_RANK = {
    "available": 3,
    "near_capacity": 2,
    "full": 0,
}

STATUS_RANK = {
    "open": 2,
    "limited": 1,
    "closed": 0,
}


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _normalize_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def candidate_sort_key(candidate: Dict[str, Any]) -> Tuple[int, int, int, int, str]:
    eta_minutes = _normalize_int(candidate.get("eta_minutes"), default=10**9)
    capacity_rank = CAPACITY_RANK.get(_normalize_text(candidate.get("capacity_status")), 0)
    status_rank = STATUS_RANK.get(_normalize_text(candidate.get("availability_status")), 0)
    sla_priority = _normalize_int(candidate.get("sla_priority"), default=0)
    clinic_id = str(candidate.get("clinic_id") or candidate.get("partner_id") or "")
    return (
        eta_minutes,
        -capacity_rank,
        -status_rank,
        -sla_priority,
        clinic_id,
    )


def rank_candidates(candidates: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    ranked = [dict(candidate) for candidate in candidates]
    ranked.sort(key=candidate_sort_key)
    for index, candidate in enumerate(ranked, start=1):
        candidate["rank"] = index
    return ranked
