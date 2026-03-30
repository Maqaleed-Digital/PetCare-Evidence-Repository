from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from petcare.ai_evidence.service import build_default_ai_evidence_service


router = APIRouter(prefix="/api/ep05/ai-evidence", tags=["ep05-ai-evidence"])


@router.post("/exports/{tenant_id}/{case_id}")
def export_case_evidence(tenant_id: str, case_id: str) -> dict:
    service = build_default_ai_evidence_service()
    return asdict(service.export_case_evidence(tenant_id=tenant_id, case_id=case_id))


@router.get("/exports/{record_id}")
def get_export(record_id: str) -> dict:
    service = build_default_ai_evidence_service()
    record = service.get_export(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="evidence_export_not_found")
    return asdict(record)


@router.get("/cases/{case_id}/exports")
def list_case_exports(case_id: str) -> dict:
    service = build_default_ai_evidence_service()
    return {
        "case_id": case_id,
        "records": [asdict(item) for item in service.list_case_exports(case_id)],
    }


@router.post("/reports/{tenant_id}/{scope_type}/{scope_id}")
def generate_governance_report(tenant_id: str, scope_type: str, scope_id: str) -> dict:
    service = build_default_ai_evidence_service()
    try:
        return asdict(service.generate_governance_report(tenant_id=tenant_id, scope_type=scope_type, scope_id=scope_id))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/reports/{record_id}")
def get_report(record_id: str) -> dict:
    service = build_default_ai_evidence_service()
    record = service.get_report(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="governance_report_not_found")
    return asdict(record)


@router.get("/reports")
def list_reports() -> dict:
    service = build_default_ai_evidence_service()
    return {
        "records": [asdict(item) for item in service.list_reports()],
    }
