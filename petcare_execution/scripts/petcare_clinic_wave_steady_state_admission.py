#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path

PACK_ID = "PETCARE-CLINIC-WAVE-STEADY-STATE-ADMISSION"
EXPECTED_BASELINE = "a0bffda0bba161bd001edadfdd4366f19c0924a4"

REPO_ROOT = Path("/Users/waheebmahmoud/dev/petcare-evidence-repository")
DOC_DIR = REPO_ROOT / "petcare_execution" / "GOVERNANCE" / "CLINIC_WAVE_STEADY_STATE_ADMISSION"
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
        raise SystemExit(f"STOP: expected 5 steady-state docs, found {len(docs)}")

    run_id = utc_run_id()
    run_dir = EVIDENCE_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    clinics = [
        {"clinic_code": "CLINIC-WAVE2-001", "wave": "WAVE_2", "admission_state": "ready_for_admission_review"},
        {"clinic_code": "CLINIC-WAVE2-002", "wave": "WAVE_2", "admission_state": "ready_for_admission_review"},
        {"clinic_code": "CLINIC-WAVEN-001", "wave": "WAVE_N", "admission_state": "ready_for_admission_review"},
        {"clinic_code": "CLINIC-WAVEN-002", "wave": "WAVE_N", "admission_state": "ready_for_admission_review"},
    ]

    admission_criteria = {
        "mandatory_criteria": [
            "hypercare_exit_review_completed",
            "no_unresolved_material_deviation",
            "override_posture_within_controlled_tolerance",
            "escalation_posture_confirmed_operational",
            "kpi_completeness_confirmed_stable",
            "partner_fallback_posture_reviewed",
            "portfolio_comparison_visibility_active",
            "steady_state_control_posture_confirmed",
        ],
        "admission_outcomes": [
            "admitted_to_steady_state",
            "remain_in_hypercare",
            "return_to_remediation",
        ],
    }

    steady_state_controls = {
        "required_controls": [
            "assistive_ai_boundary_preserved",
            "human_approval_enforcement_preserved",
            "override_capture_preserved",
            "escalation_routing_preserved",
            "kpi_reporting_preserved",
            "partner_dependency_visibility_preserved",
            "portfolio_comparison_participation_preserved",
            "remediation_reentry_path_preserved",
        ],
        "drift_rule": "material_drift_may_trigger_reclassification",
    }

    authority_model = {
        "authority_layers": [
            "portfolio_governance_authority",
            "clinic_wave_review_authority",
            "local_clinic_operating_authority",
        ],
        "portfolio_only_decisions": [
            "steady_state_admission",
            "return_to_remediation_after_failed_exit_review",
            "post_admission_reclassification_due_to_control_drift",
        ],
    }

    reporting_model = {
        "required_reporting_outputs": [
            "steady_state_admission_status",
            "last_hypercare_decision_outcome",
            "unresolved_deviation_count",
            "override_posture_status",
            "escalation_posture_status",
            "kpi_completeness_status",
            "partner_fallback_posture_status",
            "portfolio_comparison_status",
        ],
        "required_clinic_states": [
            "ready_for_admission_review",
            "admitted_to_steady_state",
            "remain_in_hypercare",
            "remediation_required",
            "post_admission_monitoring",
        ],
    }

    summary = {
        "pack_id": PACK_ID,
        "source_of_truth_commit": actual_head,
        "previous_governance_state": "clinic_wave_hypercare_governance_active",
        "new_governance_state": "clinic_wave_steady_state_admission_active",
        "wave_scope": ["WAVE_2", "WAVE_N"],
        "clinic_count": len(clinics),
        "admission_mode": "portfolio_governed_steady_state_admission",
    }

    validations = [
        ("baseline_commit_match", actual_head == EXPECTED_BASELINE),
        ("five_steady_state_docs_present", len(docs) == 5),
        ("four_clinics_in_admission_scope", len(clinics) == 4),
        ("eight_admission_criteria_defined", len(admission_criteria["mandatory_criteria"]) == 8),
        ("three_admission_outcomes_defined", len(admission_criteria["admission_outcomes"]) == 3),
        ("eight_steady_state_controls_defined", len(steady_state_controls["required_controls"]) == 8),
        ("three_authority_layers_defined", len(authority_model["authority_layers"]) == 3),
        ("eight_reporting_outputs_defined", len(reporting_model["required_reporting_outputs"]) == 8),
        ("state_transition_defined", summary["new_governance_state"] == "clinic_wave_steady_state_admission_active"),
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
    write_json(run_dir / "CLINIC_STEADY_STATE_ADMISSION_REGISTRY.json", {"clinics": clinics})
    write_json(run_dir / "STEADY_STATE_ADMISSION_CRITERIA_MODEL.json", admission_criteria)
    write_json(run_dir / "STEADY_STATE_CONTROL_MODEL.json", steady_state_controls)
    write_json(run_dir / "PORTFOLIO_ADMISSION_AUTHORITY_MODEL.json", authority_model)
    write_json(run_dir / "POST_HYPERCARE_REPORTING_MODEL.json", reporting_model)
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
    print("PETCARE-CLINIC-WAVE-STEADY-STATE-ADMISSION committed state target: clinic_wave_steady_state_admission_active")
    print("Next recommended state: multi_clinic_steady_state_governance")


if __name__ == "__main__":
    main()
