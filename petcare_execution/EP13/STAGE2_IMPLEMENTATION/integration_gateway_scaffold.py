from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


THIS_DIR = Path(__file__).resolve().parent
REGISTRY_PATH = THIS_DIR / "endpoint_family_registry.json"
SCOPE_MATRIX_PATH = THIS_DIR / "auth_scope_matrix.json"


@dataclass(frozen=True)
class GatewayRequest:
    method: str
    path: str
    partner_id: str
    tenant_id: str
    headers: Dict[str, str]
    body: Optional[Dict[str, Any]] = None
    path_params: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class GatewayResponse:
    status_code: int
    trace_id: str
    outcome: str
    payload: Dict[str, Any]


@dataclass(frozen=True)
class EndpointFamily:
    family_id: str
    path: str
    allowed_methods: List[str]
    classification: str
    partner_scope_required: bool
    tenant_scope_required: bool
    mutation_mode: str
    resource_type: str
    governance_state: str
    required_scopes: List[str] = field(default_factory=list)
    read_scopes: List[str] = field(default_factory=list)
    write_scopes: List[str] = field(default_factory=list)


FORBIDDEN_CAPABILITIES = {
    "payment_execution",
    "payout_release",
    "treasury_movement",
    "prescription_approval",
    "consultation_sign_off",
    "clinical_final_decision_submission",
    "emergency_override_closure",
    "ai_instruction_execution_against_core_runtime",
}


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_endpoint_families() -> Dict[str, EndpointFamily]:
    payload = _load_json(REGISTRY_PATH)
    families: Dict[str, EndpointFamily] = {}
    for item in payload["endpoint_families"]:
        families[item["family_id"]] = EndpointFamily(**item)
    forbidden = set(payload["forbidden_capabilities"])
    if forbidden != FORBIDDEN_CAPABILITIES:
        raise ValueError("Forbidden capability set drift detected.")
    return families


def load_scope_matrix() -> Dict[str, Any]:
    return _load_json(SCOPE_MATRIX_PATH)


def build_trace_id(request: GatewayRequest) -> str:
    request_id = request.headers.get("X-PetCare-Request-Id", "missing-request-id")
    return f"trace::{request.partner_id}::{request.tenant_id}::{request_id}"


def resolve_endpoint_family(path: str) -> str:
    if path == "/v1/partner/profile":
        return "partner_profile"
    if path == "/v1/orders":
        return "orders_collection"
    if path.startswith("/v1/orders/"):
        return "orders_item"
    if path == "/v1/referrals":
        return "referrals_collection"
    if path.startswith("/v1/referrals/"):
        return "referrals_item"
    if path == "/v1/availability":
        return "availability"
    if path == "/v1/catalog/batches":
        return "catalog_batches_collection"
    if path.startswith("/v1/catalog/batches/"):
        return "catalog_batches_item"
    if path == "/v1/webhook-subscriptions":
        return "webhook_subscriptions_collection"
    if path.endswith("/pause") and path.startswith("/v1/webhook-subscriptions/"):
        return "webhook_subscription_pause"
    if path.endswith("/resume") and path.startswith("/v1/webhook-subscriptions/"):
        return "webhook_subscription_resume"
    if path.startswith("/v1/webhook-subscriptions/"):
        return "webhook_subscription_item"
    if path.startswith("/v1/events/"):
        return "events_item"
    raise ValueError(f"Unsupported path: {path}")


def required_scopes_for_method(scope_matrix: Dict[str, Any], family_id: str, method: str) -> List[str]:
    method_map = scope_matrix["scope_matrix"][family_id][method]
    return list(method_map["scopes"])


def validate_required_headers(scope_matrix: Dict[str, Any], request: GatewayRequest) -> None:
    for header in scope_matrix["required_headers"]:
        if header not in request.headers or not request.headers[header]:
            raise ValueError(f"Missing required header: {header}")


def validate_idempotency(scope_matrix: Dict[str, Any], request: GatewayRequest) -> None:
    if request.method in scope_matrix["idempotency_required_for_methods"]:
        if request.method in {"POST", "PUT", "DELETE"} and "Idempotency-Key" not in request.headers:
            raise ValueError("Missing Idempotency-Key for controlled write method.")


def authorize_request(scope_matrix: Dict[str, Any], family_id: str, request: GatewayRequest, granted_scopes: List[str]) -> None:
    required = set(required_scopes_for_method(scope_matrix, family_id, request.method))
    if not required.issubset(set(granted_scopes)):
        raise PermissionError(f"Missing required scopes for {family_id} {request.method}: {sorted(required)}")


def build_internal_request_envelope(family: EndpointFamily, request: GatewayRequest, trace_id: str) -> Dict[str, Any]:
    return {
        "internal_request_type": family.family_id,
        "trace_id": trace_id,
        "partner_id": request.partner_id,
        "tenant_id": request.tenant_id,
        "external_method": request.method,
        "external_path": request.path,
        "governance_state": family.governance_state,
        "mutation_mode": family.mutation_mode,
        "body": request.body or {},
        "path_params": request.path_params,
        "query_params": request.query_params,
    }


def route_request(request: GatewayRequest, granted_scopes: List[str]) -> GatewayResponse:
    families = load_endpoint_families()
    scope_matrix = load_scope_matrix()
    validate_required_headers(scope_matrix, request)

    family_id = resolve_endpoint_family(request.path)
    family = families[family_id]

    if request.method not in family.allowed_methods:
        raise ValueError(f"Method {request.method} not allowed for {family_id}")

    validate_idempotency(scope_matrix, request)
    authorize_request(scope_matrix, family_id, request, granted_scopes)
    trace_id = build_trace_id(request)

    if family.classification in {"CONTROLLED_WRITE", "MIXED"} and request.method in {"POST", "PUT", "DELETE"}:
        if family.mutation_mode != "REQUEST_INTAKE_ONLY":
            raise ValueError("Governance drift: controlled write is not request-intake-only.")
        payload = build_internal_request_envelope(family, request, trace_id)
        return GatewayResponse(
            status_code=202,
            trace_id=trace_id,
            outcome="ACCEPTED_FOR_GOVERNED_INTERNAL_PROCESSING",
            payload=payload,
        )

    return GatewayResponse(
        status_code=200,
        trace_id=trace_id,
        outcome="READ_ACCESS_GRANTED",
        payload={
            "family_id": family.family_id,
            "resource_type": family.resource_type,
            "partner_id": request.partner_id,
            "tenant_id": request.tenant_id,
            "path": request.path,
            "method": request.method,
        },
    )


if __name__ == "__main__":
    example = GatewayRequest(
        method="POST",
        path="/v1/orders",
        partner_id="partner_001",
        tenant_id="tenant_001",
        headers={
            "Authorization": "Bearer example",
            "X-PetCare-Partner-Id": "partner_001",
            "X-PetCare-Request-Id": "req_001",
            "X-PetCare-Timestamp": "2026-04-01T12:00:00Z",
            "Idempotency-Key": "idem_001",
        },
        body={"external_reference": "ext_001"},
    )
    response = route_request(example, granted_scopes=["orders.write_request"])
    print(json.dumps(response.__dict__, indent=2, sort_keys=True))
