from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter

from petcare.ai_dashboard.service import build_default_ai_dashboard_service


router = APIRouter(prefix="/api/ep05/ai-dashboard", tags=["ep05-ai-dashboard"])


@router.get("/overview/{tenant_id}")
def get_governance_overview(tenant_id: str) -> dict:
    service = build_default_ai_dashboard_service()
    return asdict(service.get_governance_overview(tenant_id))


@router.get("/alerts/{tenant_id}")
def list_operational_alerts(tenant_id: str) -> dict:
    service = build_default_ai_dashboard_service()
    return {
        "tenant_id": tenant_id,
        "alerts": [asdict(item) for item in service.list_operational_alerts(tenant_id)],
    }


@router.get("/cases/{tenant_id}/{case_id}")
def get_case_governance_view(tenant_id: str, case_id: str) -> dict:
    service = build_default_ai_dashboard_service()
    return asdict(service.get_case_governance_view(tenant_id, case_id))
