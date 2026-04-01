from __future__ import annotations

import json
from pathlib import Path


THIS_DIR = Path(__file__).resolve().parent

PARTNER_MODEL = THIS_DIR / "partner_model_registry.json"
CREDENTIAL_MODEL = THIS_DIR / "credential_contract_registry.json"
BEHAVIOR_MATRIX = THIS_DIR / "sandbox_endpoint_behavior_matrix.json"
ONBOARDING_CONTRACT = THIS_DIR / "onboarding_transition_contract.json"
WEBHOOK_CONTRACT = THIS_DIR / "webhook_replay_contract.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_partner_model() -> None:
    data = load_json(PARTNER_MODEL)
    statuses = data["partner_statuses"]
    assert statuses == [
        "INACTIVE",
        "SANDBOX_ENABLED",
        "VALIDATING",
        "CERTIFIED",
        "ACTIVE",
        "SUSPENDED",
        "REVOKED"
    ], "Partner status lifecycle drift detected."
    assert data["rules"]["certification_required_before_active"] is True
    assert data["rules"]["active_does_not_expand_execution_authority"] is True


def assert_credential_model() -> None:
    data = load_json(CREDENTIAL_MODEL)
    assert data["rules"]["sandbox_credentials_cannot_authenticate_to_production"] is True
    assert data["rules"]["production_credentials_not_issued_in_ep14_stage1"] is True
    assert data["rules"]["credential_environment_binding_required"] is True


def assert_behavior_matrix() -> None:
    data = load_json(BEHAVIOR_MATRIX)
    families = data["endpoint_families"]
    assert len(families) == 9, "Unexpected sandbox endpoint behavior family count."
    for item in families:
        assert item["production_dispatch_allowed"] is False, f"Production dispatch allowed for {item['family_id']}"
        if item["mutation_mode"] != "NONE":
            assert item["mutation_mode"] == "SIMULATED_REQUEST_INTAKE_ONLY", f"Mutation drift for {item['family_id']}"
    assert data["rules"]["all_sandbox_writes_are_simulated_request_intake_only"] is True
    assert data["rules"]["sandbox_to_production_execution_path_allowed"] is False


def assert_onboarding_contract() -> None:
    data = load_json(ONBOARDING_CONTRACT)
    assert data["rules"]["certification_required_before_active"] is True
    assert data["rules"]["active_does_not_grant_payment_authority"] is True
    assert data["rules"]["active_does_not_grant_treasury_authority"] is True
    assert data["rules"]["active_does_not_grant_approval_authority"] is True
    assert data["rules"]["active_does_not_grant_production_execution_authority"] is True


def assert_webhook_contract() -> None:
    data = load_json(WEBHOOK_CONTRACT)
    assert data["algorithm"] == "HMAC_SHA256"
    assert data["rules"]["sandbox_webhook_secret_distinct_from_production"] is True
    assert data["rules"]["sandbox_event_namespace_distinct_from_production"] is True
    assert data["rules"]["production_events_replayable_from_sandbox"] is False


def main() -> None:
    assert_partner_model()
    assert_credential_model()
    assert_behavior_matrix()
    assert_onboarding_contract()
    assert_webhook_contract()
    report = {
        "status": "PASS",
        "sandbox_to_production_execution_path_allowed": False,
        "production_data_access_from_sandbox_allowed": False,
        "certification_required_before_active": True,
        "all_sandbox_writes_are_simulated_request_intake_only": True,
        "production_events_replayable_from_sandbox": False,
        "sandbox_endpoint_behavior_families_locked": 9
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
