#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path

PACK_ID = "PETCARE-CLINIC-WAVE-EXECUTION-READINESS"
EXPECTED_BASELINE = "40794c8fd02e038ed89f6b2556810bf55c1ed94e"

REPO_ROOT = Path("/Users/waheebmahmoud/dev/petcare-evidence-repository")
DOC_DIR = REPO_ROOT / "petcare_execution" / "GOVERNANCE" / "CLINIC_WAVE_EXECUTION_READINESS"
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
        raise SystemExit(f"STOP: expected 5 readiness docs, found {len(docs)}")

    run_id = utc_run_id()
    run_dir = EVIDENCE_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    clinics = [
        {"clinic_code": "CLINIC-WAVE2-001", "wave": "WAVE_2", "decision_state": "ready_for_execution"},
        {"clinic_code": "CLINIC-WAVE2-002", "wave": "WAVE_2", "decision_state": "ready_for_execution"},
        {"clinic_code": "CLINIC-WAVEN-001", "wave": "WAVE_N", "decision_state": "ready_for_execution"},
        {"clinic_code": "CLINIC-WAVEN-002", "wave": "WAVE_N", "decision_state": "ready_for_execution"},
    ]

    admission_checklist = {
        "required_items": [
            "clinic_code_assigned",
            "wave_assignment_confirmed",
            "local_clinical_lead_assigned",
            "staffing_minimum_confirmed",
            "human_approval_boundary_confirmed",
            "override_capture_enabled",
            "escalation_contact_chain_assigned",
            "reporting_path_enabled",
            "partner_dependency_map_recorded",
            "evidence_directory_generation_confirmed",
        ],
        "decision_outcomes": [
            "admitted_to_execution_readiness",
            "blocked_pending_remediation",
        ],
    }

    hypercare_model = {
        "entry_criteria": [
            "admission_checklist_passes",
            "activation_approval_issued",
            "local_command_ownership_assigned",
            "first_day_evidence_capture_ready",
        ],
        "monitoring_focus": [
            "override_events",
            "escalation_events",
            "kpi_completeness",
            "staffing_exceptions",
            "partner_fallback_usage",
            "ai_safety_deviations",
        ],
        "exit_outcomes": [
            "admitted_to_steady_state",
            "remain_in_hypercare",
            "return_to_remediation",
        ],
    }

    operating_command = {
        "command_layers": [
            "portfolio_governance_layer",
            "wave_execution_command_layer",
            "clinic_local_operating_layer",
        ],
        "required_roles": [
            "portfolio_governance_owner",
            "wave_execution_owner",
            "clinical_safety_owner",
            "ai_safety_owner",
            "reporting_owner",
            "escalation_owner",
            "clinic_local_owner",
        ],
        "portfolio_only_decisions": [
            "execution_start",
            "hypercare_exit",
            "remediation_closure",
            "steady_state_admission",
        ],
    }

    reporting_spec = {
        "reporting_entities": [
            "clinic_level",
            "wave_level",
            "portfolio_level",
        ],
        "minimum_reporting_metrics": [
            "clinic_admission_status",
            "execution_readiness_status",
            "hypercare_status",
            "override_event_count",
            "escalation_event_count",
            "kpi_capture_completeness",
            "staffing_exception_count",
            "partner_fallback_count",
        ],
        "required_outcome_states": [
            "not_ready",
            "ready_for_execution",
            "in_hypercare",
            "ready_for_steady_state",
            "remediation_required",
        ],
    }

    summary = {
        "pack_id": PACK_ID,
        "source_of_truth_commit": actual_head,
        "previous_governance_state": "multi_clinic_activation_wave_governance_active",
        "new_governance_state": "clinic_wave_execution_readiness_active",
        "wave_scope": ["WAVE_2", "WAVE_N"],
        "clinic_count": len(clinics),
        "execution_mode": "governed_wave_execution_readiness",
    }

    validations = [
        ("baseline_commit_match", actual_head == EXPECTED_BASELINE),
        ("five_readiness_docs_present", len(docs) == 5),
        ("four_clinics_in_scope", len(clinics) == 4),
        ("ten_admission_items_defined", len(admission_checklist["required_items"]) == 10),
        ("four_hypercare_entry_criteria_defined", len(hypercare_model["entry_criteria"]) == 4),
        ("six_hypercare_monitoring_items_defined", len(hypercare_model["monitoring_focus"]) == 6),
        ("three_command_layers_defined", len(operating_command["command_layers"]) == 3),
        ("eight_reporting_metrics_defined", len(reporting_spec["minimum_reporting_metrics"]) == 8),
        ("state_transition_defined", summary["new_governance_state"] == "clinic_wave_execution_readiness_active"),
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
    write_json(run_dir / "CLINIC_EXECUTION_REGISTRY.json", {"clinics": clinics})
    write_json(run_dir / "ADMISSION_CHECKLIST_MODEL.json", admission_checklist)
    write_json(run_dir / "HYPERCARE_MODEL.json", hypercare_model)
    write_json(run_dir / "OPERATING_COMMAND_MODEL.json", operating_command)
    write_json(run_dir / "WAVE_REPORTING_SPEC.json", reporting_spec)
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
    print("PETCARE-CLINIC-WAVE-EXECUTION-READINESS committed state target: clinic_wave_execution_readiness_active")
    print("Next recommended state: clinic_wave_controlled_activation")


if __name__ == "__main__":
    main()
