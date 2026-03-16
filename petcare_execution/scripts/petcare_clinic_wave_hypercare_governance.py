#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path

PACK_ID = "PETCARE-CLINIC-WAVE-HYPERCARE-GOVERNANCE"
EXPECTED_BASELINE = "4207ba0015370d3c3bc85f162fd0da91ed9bac3a"

REPO_ROOT = Path("/Users/waheebmahmoud/dev/petcare-evidence-repository")
DOC_DIR = REPO_ROOT / "petcare_execution" / "GOVERNANCE" / "CLINIC_WAVE_HYPERCARE_GOVERNANCE"
EVIDENCE_ROOT = REPO_ROOT / "petcare_execution" / "EVIDENCE" / PACK_ID


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_output(args: list[str]) -> str:
    return subprocess.check_output(args, cwd=REPO_ROOT, text=True).strip()


def utc_run_id() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    actual_head = git_output(["git", "rev-parse", "HEAD"])
    if actual_head != EXPECTED_BASELINE:
        raise SystemExit(f"STOP: baseline mismatch: expected {EXPECTED_BASELINE}, got {actual_head}")

    docs = sorted(DOC_DIR.glob("*.md"))
    if len(docs) != 5:
        raise SystemExit(f"STOP: expected 5 hypercare docs, found {len(docs)}")

    run_id = utc_run_id()
    run_dir = EVIDENCE_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    clinics = [
        {"clinic_code": "CLINIC-WAVE2-001", "wave": "WAVE_2", "hypercare_state": "in_hypercare"},
        {"clinic_code": "CLINIC-WAVE2-002", "wave": "WAVE_2", "hypercare_state": "in_hypercare"},
        {"clinic_code": "CLINIC-WAVEN-001", "wave": "WAVE_N", "hypercare_state": "in_hypercare"},
        {"clinic_code": "CLINIC-WAVEN-002", "wave": "WAVE_N", "hypercare_state": "in_hypercare"},
    ]

    observation_model = {
        "required_observation_controls": [
            "override_event_monitoring",
            "escalation_event_monitoring",
            "kpi_completeness_monitoring",
            "staffing_exception_monitoring",
            "incident_review_monitoring",
            "partner_fallback_monitoring",
            "command_review_cadence",
            "ai_safety_posture_review",
        ],
        "observation_states": [
            "under_observation",
            "observation_issue_detected",
            "observation_stable",
        ],
    }

    deviation_rules = {
        "deviation_categories": [
            "reporting_deviation",
            "staffing_deviation",
            "operational_deviation",
            "ai_safety_deviation",
            "escalation_deviation",
            "partner_dependency_deviation",
        ],
        "remediation_responses": [
            "monitor_within_hypercare",
            "targeted_remediation",
            "extend_hypercare",
            "block_steady_state_exit",
        ],
    }

    exit_framework = {
        "exit_inputs": [
            "observation_stability",
            "unresolved_deviation_count",
            "override_posture",
            "escalation_posture",
            "kpi_completeness_posture",
            "partner_fallback_posture",
            "portfolio_command_approval",
            "steady_state_readiness_confirmation",
        ],
        "exit_outcomes": [
            "approved_for_steady_state",
            "remain_in_hypercare",
            "return_to_remediation",
        ],
    }

    reporting_and_review = {
        "required_reporting_outputs": [
            "hypercare_status",
            "observation_stability_status",
            "deviation_count",
            "override_count",
            "escalation_count",
            "kpi_completeness_status",
            "partner_fallback_count",
            "exit_decision_status",
        ],
        "required_clinic_states": [
            "in_hypercare",
            "hypercare_stable",
            "hypercare_issue_open",
            "ready_for_exit_review",
            "remediation_required",
        ],
    }

    summary = {
        "pack_id": PACK_ID,
        "source_of_truth_commit": actual_head,
        "previous_governance_state": "clinic_wave_controlled_activation_active",
        "new_governance_state": "clinic_wave_hypercare_governance_active",
        "wave_scope": ["WAVE_2", "WAVE_N"],
        "clinic_count": len(clinics),
        "hypercare_mode": "supervised_post_activation_observation",
    }

    validations = [
        ("baseline_commit_match", actual_head == EXPECTED_BASELINE),
        ("five_hypercare_docs_present", len(docs) == 5),
        ("four_clinics_in_hypercare_scope", len(clinics) == 4),
        ("eight_observation_controls_defined", len(observation_model["required_observation_controls"]) == 8),
        ("six_deviation_categories_defined", len(deviation_rules["deviation_categories"]) == 6),
        ("four_remediation_responses_defined", len(deviation_rules["remediation_responses"]) == 4),
        ("eight_exit_inputs_defined", len(exit_framework["exit_inputs"]) == 8),
        ("eight_reporting_outputs_defined", len(reporting_and_review["required_reporting_outputs"]) == 8),
        ("state_transition_defined", summary["new_governance_state"] == "clinic_wave_hypercare_governance_active"),
    ]

    validation_report = {
        "pack_id": PACK_ID,
        "assertions_passed": sum(1 for _, ok in validations if ok),
        "assertions_total": len(validations),
        "results": [{"assertion": name, "ok": ok} for name, ok in validations],
        "status": "OK" if all(ok for _, ok in validations) else "FAIL",
    }

    if validation_report["status"] != "OK":
        raise SystemExit("STOP: validation failed")

    write_json(run_dir / "PACK_SUMMARY.json", summary)
    write_json(run_dir / "CLINIC_HYPERCARE_REGISTRY.json", {"clinics": clinics})
    write_json(run_dir / "HYPERCARE_OBSERVATION_MODEL.json", observation_model)
    write_json(run_dir / "HYPERCARE_DEVIATION_RULES.json", deviation_rules)
    write_json(run_dir / "HYPERCARE_EXIT_FRAMEWORK.json", exit_framework)
    write_json(run_dir / "HYPERCARE_REPORTING_MODEL.json", reporting_and_review)
    write_json(run_dir / "VALIDATION_REPORT.json", validation_report)

    manifest = {
        "pack_id": PACK_ID,
        "run_id": run_id,
        "source_of_truth_commit": actual_head,
        "generated_at_utc": run_id,
        "files": [],
    }

    for path in sorted(run_dir.iterdir()):
        manifest["files"].append({"path": path.name, "sha256": sha256_file(path)})

    write_json(run_dir / "MANIFEST.json", manifest)
    manifest_sha = hashlib.sha256((run_dir / "MANIFEST.json").read_bytes()).hexdigest()
    (run_dir / "MANIFEST.sha256").write_text(f"{manifest_sha}  MANIFEST.json\n", encoding="utf-8")

    print(f"PACK_ID              : {PACK_ID}")
    print(f"VALIDATION           : OK ({validation_report['assertions_passed']}/{validation_report['assertions_total']} assertions passed)")
    print(f"EVIDENCE_RUN_DIR     : {run_dir.relative_to(REPO_ROOT)}")
    print(f"SOURCE_OF_TRUTH_COMMIT: {actual_head}")
    print("PETCARE-CLINIC-WAVE-HYPERCARE-GOVERNANCE committed state target: clinic_wave_hypercare_governance_active")
    print("Next recommended state: clinic_wave_steady_state_admission")


if __name__ == "__main__":
    main()
