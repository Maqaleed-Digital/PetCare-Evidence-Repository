from __future__ import annotations

from typing import Any, Dict, List


def build_explanation(candidate: Dict[str, Any]) -> Dict[str, Any]:
    eta_minutes = candidate.get("eta_minutes")
    capacity_status = candidate.get("capacity_status")
    availability_status = candidate.get("availability_status")
    sla_priority = candidate.get("sla_priority")
    readiness = bool(candidate.get("emergency_ready"))

    reasons: List[str] = []
    reasons.append(f"ETA {eta_minutes} minutes")
    reasons.append(f"capacity {capacity_status}")
    reasons.append(f"status {availability_status}")
    reasons.append(f"SLA priority {sla_priority}")
    reasons.append("emergency ready true" if readiness else "emergency ready false")

    return {
        "summary": "; ".join(reasons),
        "factors": {
            "eta_minutes": eta_minutes,
            "capacity_status": capacity_status,
            "availability_status": availability_status,
            "sla_priority": sla_priority,
            "emergency_ready": readiness,
        },
        "reasons": reasons,
    }
