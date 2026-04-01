from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class ExternalAuditRecord:
    actor_type: str
    partner_id: str
    tenant_id: str
    request_id: str
    trace_id: str
    endpoint: str
    method: str
    response_code: int
    auth_method: str
    policy_version: str
    idempotency_key: Optional[str]
    created_at: str


@dataclass(frozen=True)
class TraceChain:
    trace_id: str
    partner_id: str
    tenant_id: str
    external_request_id: str
    internal_request_id: Optional[str]
    approval_record_id: Optional[str]
    execution_record_id: Optional[str]
    outcome_record_id: Optional[str]
    created_at: str


def build_external_audit_record(
    partner_id: str,
    tenant_id: str,
    request_id: str,
    trace_id: str,
    endpoint: str,
    method: str,
    response_code: int,
    auth_method: str,
    policy_version: str,
    idempotency_key: Optional[str] = None,
) -> ExternalAuditRecord:
    return ExternalAuditRecord(
        actor_type="external_partner_system",
        partner_id=partner_id,
        tenant_id=tenant_id,
        request_id=request_id,
        trace_id=trace_id,
        endpoint=endpoint,
        method=method,
        response_code=response_code,
        auth_method=auth_method,
        policy_version=policy_version,
        idempotency_key=idempotency_key,
        created_at=utc_now_iso(),
    )


def build_trace_chain(
    trace_id: str,
    partner_id: str,
    tenant_id: str,
    external_request_id: str,
    internal_request_id: Optional[str] = None,
    approval_record_id: Optional[str] = None,
    execution_record_id: Optional[str] = None,
    outcome_record_id: Optional[str] = None,
) -> TraceChain:
    return TraceChain(
        trace_id=trace_id,
        partner_id=partner_id,
        tenant_id=tenant_id,
        external_request_id=external_request_id,
        internal_request_id=internal_request_id,
        approval_record_id=approval_record_id,
        execution_record_id=execution_record_id,
        outcome_record_id=outcome_record_id,
        created_at=utc_now_iso(),
    )


def to_json(payload: object) -> str:
    return json.dumps(asdict(payload), indent=2, sort_keys=True)


def build_governed_request_audit_bundle(
    partner_id: str,
    tenant_id: str,
    request_id: str,
    trace_id: str,
    endpoint: str,
    method: str,
    auth_method: str,
    policy_version: str,
    idempotency_key: Optional[str],
    internal_request_id: str,
) -> Dict[str, object]:
    audit = build_external_audit_record(
        partner_id=partner_id,
        tenant_id=tenant_id,
        request_id=request_id,
        trace_id=trace_id,
        endpoint=endpoint,
        method=method,
        response_code=202,
        auth_method=auth_method,
        policy_version=policy_version,
        idempotency_key=idempotency_key,
    )
    chain = build_trace_chain(
        trace_id=trace_id,
        partner_id=partner_id,
        tenant_id=tenant_id,
        external_request_id=request_id,
        internal_request_id=internal_request_id,
        approval_record_id=None,
        execution_record_id=None,
        outcome_record_id=None,
    )
    return {
        "audit_record": asdict(audit),
        "trace_chain": asdict(chain),
    }


if __name__ == "__main__":
    bundle = build_governed_request_audit_bundle(
        partner_id="partner_001",
        tenant_id="tenant_001",
        request_id="req_001",
        trace_id="trace::partner_001::tenant_001::req_001",
        endpoint="/v1/orders",
        method="POST",
        auth_method="oauth2_client_credentials",
        policy_version="ep13_stage2_v1",
        idempotency_key="idem_001",
        internal_request_id="intreq_001",
    )
    print(json.dumps(bundle, indent=2, sort_keys=True))
