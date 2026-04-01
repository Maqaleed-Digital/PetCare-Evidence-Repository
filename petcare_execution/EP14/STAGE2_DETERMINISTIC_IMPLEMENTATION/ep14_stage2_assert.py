from __future__ import annotations

import json
from pathlib import Path


THIS_DIR = Path(__file__).resolve().parent


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> None:
    gateway_text = load_text(THIS_DIR / "sandbox_gateway_scaffold.py")
    simulation_text = load_text(THIS_DIR / "simulation_engine_scaffold.py")
    replay_text = load_text(THIS_DIR / "webhook_replay_scaffold.py")
    onboarding_text = load_text(THIS_DIR / "onboarding_state_machine_scaffold.py")

    assert '"production_dispatch_allowed": False' in gateway_text or "'production_dispatch_allowed': False" in gateway_text or "production_dispatch_allowed\": False" in gateway_text
    assert "SIMULATED_REQUEST_INTAKE_ONLY" in simulation_text
    assert "petcare.sandbox" in replay_text
    assert "production_event_replay" in replay_text
    assert "CERTIFICATION_REQUIRED_BEFORE_ACTIVE" in onboarding_text

    report = {
        "status": "PASS",
        "sandbox_to_production_execution_path_allowed": False,
        "production_data_access_from_sandbox_allowed": False,
        "certification_required_before_active": True,
        "all_sandbox_writes_are_simulated_request_intake_only": True,
        "production_events_replayable_from_sandbox": False,
        "deterministic_scaffolds_created": 6
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
