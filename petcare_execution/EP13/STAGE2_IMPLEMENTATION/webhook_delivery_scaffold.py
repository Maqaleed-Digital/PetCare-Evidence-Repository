from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


ALLOWED_EVENT_TYPES = [
    "order.created",
    "order.updated",
    "referral.created",
    "referral.updated",
    "availability.updated",
    "catalog.batch.completed",
    "webhook.subscription.disabled",
    "settlement.generated",
    "dispute.opened",
]


@dataclass(frozen=True)
class WebhookEnvelope:
    event_id: str
    event_type: str
    occurred_at: str
    partner_id: str
    tenant_id: str
    trace_id: str
    payload: Dict[str, Any]
    payload_hash: str

    def as_json(self) -> str:
        return json.dumps(
            {
                "event_id": self.event_id,
                "event_type": self.event_type,
                "occurred_at": self.occurred_at,
                "partner_id": self.partner_id,
                "tenant_id": self.tenant_id,
                "trace_id": self.trace_id,
                "payload": self.payload,
                "payload_hash": self.payload_hash,
            },
            sort_keys=True,
            separators=(",", ":"),
        )


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def payload_hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_envelope(
    event_id: str,
    event_type: str,
    partner_id: str,
    tenant_id: str,
    trace_id: str,
    payload: Dict[str, Any],
) -> WebhookEnvelope:
    if event_type not in ALLOWED_EVENT_TYPES:
        raise ValueError(f"Unsupported event type: {event_type}")
    return WebhookEnvelope(
        event_id=event_id,
        event_type=event_type,
        occurred_at=utc_now_iso(),
        partner_id=partner_id,
        tenant_id=tenant_id,
        trace_id=trace_id,
        payload=payload,
        payload_hash=payload_hash(payload),
    )


def sign_webhook(secret: str, timestamp: str, raw_body: str) -> str:
    signing_basis = f"{timestamp}.{raw_body}".encode("utf-8")
    return hmac.new(secret.encode("utf-8"), signing_basis, hashlib.sha256).hexdigest()


def verify_webhook_signature(secret: str, timestamp: str, raw_body: str, provided_signature: str) -> bool:
    expected = sign_webhook(secret=secret, timestamp=timestamp, raw_body=raw_body)
    return hmac.compare_digest(expected, provided_signature)


def build_delivery_attempt(
    envelope: WebhookEnvelope,
    subscription_id: str,
    signature_key_id: str,
    attempt_count: int,
    delivery_status: str,
    next_retry_at: Optional[str] = None,
) -> Dict[str, Any]:
    if delivery_status not in {"PENDING", "DELIVERED", "RETRY_SCHEDULED", "FAILED", "DISABLED"}:
        raise ValueError(f"Unsupported delivery status: {delivery_status}")
    return {
        "event_id": envelope.event_id,
        "event_type": envelope.event_type,
        "subscription_id": subscription_id,
        "delivery_status": delivery_status,
        "attempt_count": attempt_count,
        "last_attempt_at": utc_now_iso(),
        "next_retry_at": next_retry_at,
        "trace_id": envelope.trace_id,
        "payload_hash": envelope.payload_hash,
        "signature_key_id": signature_key_id,
    }


if __name__ == "__main__":
    env = build_envelope(
        event_id="evt_001",
        event_type="order.created",
        partner_id="partner_001",
        tenant_id="tenant_001",
        trace_id="trace::partner_001::tenant_001::req_001",
        payload={"order_id": "ord_001", "status": "REQUEST_RECEIVED"},
    )
    body = env.as_json()
    timestamp = utc_now_iso()
    signature = sign_webhook(secret="secret_001", timestamp=timestamp, raw_body=body)
    verified = verify_webhook_signature(secret="secret_001", timestamp=timestamp, raw_body=body, provided_signature=signature)
    attempt = build_delivery_attempt(
        envelope=env,
        subscription_id="sub_001",
        signature_key_id="sigkey_001",
        attempt_count=1,
        delivery_status="PENDING",
    )
    print(json.dumps({"verified": verified, "attempt": attempt}, indent=2, sort_keys=True))
