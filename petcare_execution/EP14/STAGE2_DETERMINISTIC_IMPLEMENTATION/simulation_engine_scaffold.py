from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Any, Dict


SIMULATED_BEHAVIORS = {
    "orders_collection": "SIMULATE_REQUEST_ACCEPTED",
    "referrals_collection": "SIMULATE_REQUEST_ACCEPTED",
    "availability": "SIMULATE_REQUEST_PROCESSED",
    "catalog_batches_collection": "SIMULATE_BATCH_VALIDATION",
    "webhook_subscriptions_collection": "SIMULATE_SUBSCRIPTION_LIFECYCLE",
    "webhook_subscription_pause": "SIMULATE_SUBSCRIPTION_PAUSE",
    "webhook_subscription_resume": "SIMULATE_SUBSCRIPTION_RESUME",
    "webhook_subscription_item": "SIMULATE_SUBSCRIPTION_DISABLE",
    "events_item": "REPLAY_SANDBOX_EVENT_ONLY",
}


@dataclass(frozen=True)
class SimulationResult:
    family_id: str
    sandbox_trace_id: str
    behavior: str
    status: str
    payload: Dict[str, Any]


def build_sandbox_trace_id(partner_id: str, tenant_id: str, request_id: str) -> str:
    return f"sandbox-trace::{partner_id}::{tenant_id}::{request_id}"


def simulate(family_id: str, partner_id: str, tenant_id: str, request_id: str, body: Dict[str, Any]) -> SimulationResult:
    if family_id not in SIMULATED_BEHAVIORS:
        raise ValueError(f"Unsupported family_id: {family_id}")
    behavior = SIMULATED_BEHAVIORS[family_id]
    trace_id = build_sandbox_trace_id(partner_id=partner_id, tenant_id=tenant_id, request_id=request_id)

    if behavior == "REPLAY_SANDBOX_EVENT_ONLY":
        status = "REPLAY_READY"
    elif behavior == "SIMULATE_BATCH_VALIDATION":
        status = "SIMULATED_VALIDATION_COMPLETE"
    elif behavior == "SIMULATE_REQUEST_PROCESSED":
        status = "SIMULATED_REQUEST_PROCESSED"
    else:
        status = "SIMULATED_REQUEST_ACCEPTED"

    payload = {
        "family_id": family_id,
        "trace_id": trace_id,
        "simulated": True,
        "mutation_mode": "SIMULATED_REQUEST_INTAKE_ONLY",
        "body": body,
        "production_dispatch_allowed": False,
    }
    return SimulationResult(
        family_id=family_id,
        sandbox_trace_id=trace_id,
        behavior=behavior,
        status=status,
        payload=payload,
    )


if __name__ == "__main__":
    result = simulate(
        family_id="orders_collection",
        partner_id="partner_001",
        tenant_id="tenant_001",
        request_id="req_001",
        body={"external_reference": "ext_001"},
    )
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
