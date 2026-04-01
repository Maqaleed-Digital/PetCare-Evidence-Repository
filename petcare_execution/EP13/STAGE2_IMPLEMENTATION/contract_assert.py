from __future__ import annotations

import json
from pathlib import Path


THIS_DIR = Path(__file__).resolve().parent
REGISTRY_PATH = THIS_DIR / "endpoint_family_registry.json"
SCOPE_MATRIX_PATH = THIS_DIR / "auth_scope_matrix.json"

EXPECTED_FAMILY_IDS = {
    "partner_profile",
    "orders_collection",
    "orders_item",
    "referrals_collection",
    "referrals_item",
    "availability",
    "catalog_batches_collection",
    "catalog_batches_item",
    "webhook_subscriptions_collection",
    "webhook_subscription_pause",
    "webhook_subscription_resume",
    "webhook_subscription_item",
    "events_item",
}

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

EXPECTED_SCOPES = {
    "partner.read",
    "orders.read",
    "orders.write_request",
    "referrals.read",
    "referrals.write_request",
    "availability.write",
    "catalog.write",
    "webhooks.manage",
    "events.read",
}

ALLOWED_WEBHOOK_EVENTS = {
    "order.created",
    "order.updated",
    "referral.created",
    "referral.updated",
    "availability.updated",
    "catalog.batch.completed",
    "webhook.subscription.disabled",
    "settlement.generated",
    "dispute.opened",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_registry() -> None:
    registry = load_json(REGISTRY_PATH)
    families = registry["endpoint_families"]
    family_ids = {item["family_id"] for item in families}
    assert family_ids == EXPECTED_FAMILY_IDS, f"Endpoint family drift: {sorted(family_ids)}"
    assert len(families) == 13, f"Expected 13 endpoint families, found {len(families)}"

    forbidden = set(registry["forbidden_capabilities"])
    assert forbidden == FORBIDDEN_CAPABILITIES, "Forbidden capability drift detected."

    for family in families:
        assert family["partner_scope_required"] is True, f"Partner scope not required for {family['family_id']}"
        assert family["tenant_scope_required"] is True, f"Tenant scope not required for {family['family_id']}"
        if family["classification"] in {"CONTROLLED_WRITE", "MIXED"} and any(
            method in {"POST", "PUT", "DELETE"} for method in family["allowed_methods"]
        ):
            assert family["mutation_mode"] == "REQUEST_INTAKE_ONLY", f"Mutation mode drift for {family['family_id']}"


def assert_scope_matrix() -> None:
    matrix = load_json(SCOPE_MATRIX_PATH)
    assert set(matrix["required_headers"]) == {
        "Authorization",
        "X-PetCare-Partner-Id",
        "X-PetCare-Request-Id",
        "X-PetCare-Timestamp",
    }, "Required headers drift detected."

    scope_values = set()
    for family_id, method_map in matrix["scope_matrix"].items():
        assert family_id in EXPECTED_FAMILY_IDS, f"Unknown family in scope matrix: {family_id}"
        for method, config in method_map.items():
            assert config["partner_scope_required"] is True, f"Partner scope missing in {family_id} {method}"
            assert config["tenant_scope_required"] is True, f"Tenant scope missing in {family_id} {method}"
            scope_values.update(config["scopes"])
            if method in {"POST", "PUT", "DELETE"}:
                assert config.get("governed_request_intake_only", False) is True, f"Governed write drift in {family_id} {method}"

    assert EXPECTED_SCOPES.issubset(scope_values), f"Scope drift detected: {sorted(scope_values)}"

    webhook_headers = set(matrix["webhook_signing"]["required_headers"])
    assert webhook_headers == {
        "X-PetCare-Signature",
        "X-PetCare-Signature-Timestamp",
        "X-PetCare-Event-Id",
    }, "Webhook signing header drift detected."
    assert matrix["webhook_signing"]["algorithm"] == "HMAC_SHA256", "Webhook algorithm drift detected."


def main() -> None:
    assert_registry()
    assert_scope_matrix()
    report = {
        "status": "PASS",
        "endpoint_families_locked": 13,
        "forbidden_capabilities_exposed": False,
        "all_controlled_writes_request_intake_only": True,
        "partner_scope_required": True,
        "tenant_scope_required": True,
        "allowed_webhook_events": sorted(ALLOWED_WEBHOOK_EVENTS),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
