from __future__ import annotations

import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from simulation_engine_scaffold import simulate


REQUIRED_HEADERS = [
    "Authorization",
    "X-PetCare-Partner-Id",
    "X-PetCare-Request-Id",
    "X-PetCare-Timestamp",
]

FAMILY_BY_PATH = {
    ("/sandbox/v1/orders", "POST"): "orders_collection",
    ("/sandbox/v1/referrals", "POST"): "referrals_collection",
    ("/sandbox/v1/availability", "PUT"): "availability",
    ("/sandbox/v1/catalog/batches", "POST"): "catalog_batches_collection",
    ("/sandbox/v1/webhook-subscriptions", "GET"): "webhook_subscriptions_collection",
    ("/sandbox/v1/webhook-subscriptions", "POST"): "webhook_subscriptions_collection",
    ("/sandbox/v1/webhook-subscriptions/pause", "POST"): "webhook_subscription_pause",
    ("/sandbox/v1/webhook-subscriptions/resume", "POST"): "webhook_subscription_resume",
    ("/sandbox/v1/webhook-subscriptions", "DELETE"): "webhook_subscription_item",
    ("/sandbox/v1/events", "GET"): "events_item",
}


@dataclass(frozen=True)
class SandboxGatewayRequest:
    method: str
    path: str
    partner_id: str
    tenant_id: str
    headers: Dict[str, str]
    body: Dict[str, Any]


def validate_headers(headers: Dict[str, str]) -> None:
    for header in REQUIRED_HEADERS:
        if not headers.get(header):
            raise ValueError(f"Missing required header: {header}")


def validate_sandbox_environment(headers: Dict[str, str]) -> None:
    if headers.get("X-PetCare-Environment", "SANDBOX") != "SANDBOX":
        raise ValueError("Sandbox gateway accepts SANDBOX environment only.")


def resolve_family(path: str, method: str) -> str:
    key = (path, method)
    if key not in FAMILY_BY_PATH:
        raise ValueError(f"Unsupported sandbox endpoint: {method} {path}")
    return FAMILY_BY_PATH[key]


def route_request(request: SandboxGatewayRequest) -> Dict[str, Any]:
    validate_headers(request.headers)
    validate_sandbox_environment(request.headers)
    family_id = resolve_family(path=request.path, method=request.method)
    result = simulate(
        family_id=family_id,
        partner_id=request.partner_id,
        tenant_id=request.tenant_id,
        request_id=request.headers["X-PetCare-Request-Id"],
        body=request.body,
    )
    return {
        "gateway_mode": "SANDBOX_ONLY",
        "production_dispatch_allowed": False,
        "result": asdict(result),
    }


if __name__ == "__main__":
    example = SandboxGatewayRequest(
        method="POST",
        path="/sandbox/v1/orders",
        partner_id="partner_001",
        tenant_id="tenant_001",
        headers={
            "Authorization": "Bearer sandbox",
            "X-PetCare-Partner-Id": "partner_001",
            "X-PetCare-Request-Id": "req_001",
            "X-PetCare-Timestamp": "2026-04-01T12:30:00Z",
            "X-PetCare-Environment": "SANDBOX",
        },
        body={"external_reference": "ext_001"},
    )
    print(json.dumps(route_request(example), indent=2, sort_keys=True))
