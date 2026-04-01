from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict


ALLOWED_EVENT_TYPES = [
    "order.created",
    "order.updated",
    "referral.created",
    "referral.updated",
    "availability.updated",
    "catalog.batch.completed",
    "webhook.subscription.disabled",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class SandboxReplayEnvelope:
    event_id: str
    event_type: str
    sandbox_trace_id: str
    occurred_at: str
    payload: Dict[str, Any]
    event_namespace: str


def build_envelope(event_id: str, event_type: str, sandbox_trace_id: str, payload: Dict[str, Any]) -> SandboxReplayEnvelope:
    if event_type not in ALLOWED_EVENT_TYPES:
        raise ValueError(f"Unsupported sandbox replay event type: {event_type}")
    return SandboxReplayEnvelope(
        event_id=event_id,
        event_type=event_type,
        sandbox_trace_id=sandbox_trace_id,
        occurred_at=utc_now_iso(),
        payload=payload,
        event_namespace="petcare.sandbox",
    )


def sign_envelope(secret: str, timestamp: str, raw_body: str) -> str:
    signing_basis = f"{timestamp}.{raw_body}".encode("utf-8")
    return hmac.new(secret.encode("utf-8"), signing_basis, hashlib.sha256).hexdigest()


def build_delivery_attempt(subscription_id: str, envelope: SandboxReplayEnvelope) -> Dict[str, Any]:
    return {
        "subscription_id": subscription_id,
        "event_id": envelope.event_id,
        "event_type": envelope.event_type,
        "sandbox_trace_id": envelope.sandbox_trace_id,
        "occurred_at": envelope.occurred_at,
        "delivery_status": "REPLAY_ATTEMPTED",
        "production_event_replay": False,
    }


if __name__ == "__main__":
    envelope = build_envelope(
        event_id="evt_001",
        event_type="order.created",
        sandbox_trace_id="sandbox-trace::partner_001::tenant_001::req_001",
        payload={"order_id": "ord_001"},
    )
    raw_body = json.dumps(asdict(envelope), sort_keys=True, separators=(",", ":"))
    timestamp = utc_now_iso()
    signature = sign_envelope(secret="sandbox-secret", timestamp=timestamp, raw_body=raw_body)
    delivery = build_delivery_attempt(subscription_id="sub_001", envelope=envelope)
    print(json.dumps({"delivery": delivery, "envelope": asdict(envelope), "signature": signature}, indent=2, sort_keys=True))
