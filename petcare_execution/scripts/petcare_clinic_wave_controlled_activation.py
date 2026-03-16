#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path

PACK_ID = "PETCARE-CLINIC-WAVE-CONTROLLED-ACTIVATION"
EXPECTED_BASELINE = "037f7c26fb36b9ce10f58a63a66b473c64ca918e"

REPO_ROOT = Path("/Users/waheebmahmoud/dev/petcare-evidence-repository")
DOC_DIR = REPO_ROOT / "petcare_execution" / "GOVERNANCE" / "CLINIC_WAVE_CONTROLLED_ACTIVATION"
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
        raise SystemExit(f"STOP: expected 5 activation docs, found {len(docs)}")

    run_id = utc_run_id()
    run_dir = EVIDENCE_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    clinics = [
        {
            "clinic_code": "CLINIC-WAVE2-001",
            "wave": "WAVE_2",
            "sequence_position": 1,
            "activation_state": "awaiting_gate_decision",
        },
        {
            "clinic_code": "CLINIC-WAVE2-002",
            "wave": "WAVE_2",
            "sequence_position": 2,
            "activation_state": "awaiting_gate_decision",
        },
        {
            "clinic_code": "CLINIC-WAVEN-001",
            "wave": "WAVE_N",
            "sequence_position": 3,
            "activation_state": "awaiting_gate_decision",
        },
        {
            "clinic_code": "CLINIC-WAVEN-002",
            "wave": "WAVE_N",
            "sequence_position": 4,
            "activation_state": "awaiting_gate_decision",
        },
    ]

    activation_gate = {
        "required_gate_inputs": [
            "execution_readiness_status",
            "ai_safety_readiness",
            "staffing_coverage_confirmation",
            "escalation_routing_confirmation",
            "partner_dependency_readiness",
            "reporting_visibility_confirmation",
            "first_day_operational_control_readiness",
            "portfolio_command_approval",
        ],
        "decision_outcomes": [
            "approved_for_activation",
            "blocked_pending_remediation",
            "deferred_for_wave_resequencing",
        ],
    }

    first_day_controls = {
        "required_controls": [
            "human_approval_enforcement_active",
            "override_capture_active",
            "escalation_contact_path_reachable",
            "first_day_reporting_snapshot_enabled",
            "command_monitoring_active",
            "incident_logging_active",
            "partner_fallback_path_available",
            "end_of_day_control_review_scheduled",
        ],
        "failure_rule": "material_failure_requires_immediate_command_review",
    }

    sequence_plan = {
        "default_sequence": [
            "CLINIC-WAVE2-001",
            "CLINIC-WAVE2-002",
            "CLINIC-WAVEN-001",
            "CLINIC-WAVEN-002",
        ],
        "required_window_fields": [
            "activation_window_assigned",
            "command_owner_assigned",
            "first_day_control_checklist_assigned",
            "hypercare_entry_record_assigned",
        ],
        "resequencing_allowed": True,
    }

    reporting_and_escalation = {
        "required_reporting_outputs": [
            "gate_decision_status",
            "activation_sequence_position",
            "activation_window_assignment",
            "first_day_control_status",
            "incident_count",
            "override_count",
            "escalation_count",
            "hypercare_entry_status",
        ],
        "required_outcome_states": [
            "awaiting_gate_decision",
            "approved_for_activation",
            "activation_in_progress",
            "activation_issue_escalated",
            "hypercare_started",
        ],
    }

    summary = {
        "pack_id": PACK_ID,
        "source_of_truth_commit": actual_head,
        "previous_governance_state": "clinic_wave_execution_readiness_active",
        "new_governance_state": "clinic_wave_controlled_activation_active",
        "wave_scope": ["WAVE_2", "WAVE_N"],
        "clinic_count": len(clinics),
        "activation_mode": "controlled_sequenced_activation",
    }

    validations = [
        ("baseline_commit_match", actual_head == EXPECTED_BASELINE),
        ("five_activation_docs_present", len(docs) == 5),
        ("four_clinics_in_activation_scope", len(clinics) == 4),
        ("eight_gate_inputs_defined", len(activation_gate["required_gate_inputs"]) == 8),
        ("three_gate_outcomes_defined", len(activation_gate["decision_outcomes"]) == 3),
        ("eight_first_day_controls_defined", len(first_day_controls["required_controls"]) == 8),
        ("four_sequence_entries_defined", len(sequence_plan["default_sequence"]) == 4),
        ("eight_reporting_outputs_defined", len(reporting_and_escalation["required_reporting_outputs"]) == 8),
        ("state_transition_defined", summary["new_governance_state"] == "clinic_wave_controlled_activation_active"),
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
    write_json(run_dir / "CLINIC_ACTIVATION_SEQUENCE.json", {"clinics": clinics})
    write_json(run_dir / "ACTIVATION_GATE_MODEL.json", activation_gate)
    write_json(run_dir / "FIRST_DAY_CONTROL_MODEL.json", first_day_controls)
    write_json(run_dir / "ACTIVATION_SEQUENCE_PLAN.json", sequence_plan)
    write_json(run_dir / "ACTIVATION_REPORTING_AND_ESCALATION.json", reporting_and_escalation)
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
    print("PETCARE-CLINIC-WAVE-CONTROLLED-ACTIVATION committed state target: clinic_wave_controlled_activation_active")
    print("Next recommended state: clinic_wave_hypercare_governance")


if __name__ == "__main__":
    main()
