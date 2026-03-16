#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path

PACK_ID = "PETCARE-MULTI-CLINIC-STEADY-STATE-GOVERNANCE"
EXPECTED_BASELINE = "f598743438b3884ce2f3a4e19b2c3a7d465e9a1b"

REPO_ROOT = Path("/Users/waheebmahmoud/dev/petcare-evidence-repository")
DOC_DIR = REPO_ROOT / "petcare_execution" / "GOVERNANCE" / "MULTI_CLINIC_STEADY_STATE_GOVERNANCE"
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
        raise SystemExit(f"STOP: expected 5 multi-clinic steady-state docs, found {len(docs)}")

    run_id = utc_run_id()
    run_dir = EVIDENCE_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    clinics = [
        {"clinic_code": "CLINIC-LIVE-BASELINE-001", "portfolio_state": "steady_state_operational"},
        {"clinic_code": "CLINIC-WAVE2-001", "portfolio_state": "steady_state_operational"},
        {"clinic_code": "CLINIC-WAVE2-002", "portfolio_state": "steady_state_operational"},
        {"clinic_code": "CLINIC-WAVEN-001", "portfolio_state": "steady_state_operational"},
        {"clinic_code": "CLINIC-WAVEN-002", "portfolio_state": "steady_state_operational"},
    ]

    control_posture = {
        "required_cross_clinic_controls": [
            "assistive_ai_boundary_preserved",
            "human_approval_enforcement_preserved",
            "override_capture_preserved",
            "escalation_routing_preserved",
            "kpi_reporting_preserved",
            "partner_dependency_visibility_preserved",
            "portfolio_comparison_participation_preserved",
            "remediation_reentry_path_preserved",
        ],
        "control_posture_states": [
            "control_posture_compliant",
            "control_posture_watch",
            "control_posture_issue_open",
        ],
    }

    operating_review = {
        "required_review_domains": [
            "admission_status",
            "override_posture",
            "escalation_posture",
            "kpi_completeness",
            "partner_fallback_posture",
            "staffing_exception_posture",
            "drift_posture",
            "remediation_exposure",
        ],
        "comparison_groups": [
            "baseline_live_clinic",
            "newly_admitted_steady_state_clinics",
            "clinics_on_watch",
            "clinics_under_remediation_review",
        ],
    }

    drift_governance = {
        "drift_categories": [
            "reporting_drift",
            "operational_drift",
            "ai_safety_drift",
            "escalation_drift",
            "partner_dependency_drift",
            "kpi_drift",
        ],
        "governance_responses": [
            "portfolio_watch",
            "targeted_remediation",
            "steady_state_reclassification",
            "controlled_reentry_to_remediation",
        ],
    }

    reporting_visibility = {
        "required_reporting_outputs": [
            "clinic_steady_state_status",
            "control_posture_status",
            "override_posture_status",
            "escalation_posture_status",
            "kpi_completeness_status",
            "partner_fallback_posture_status",
            "drift_status",
            "remediation_status",
        ],
        "required_clinic_states": [
            "steady_state_operational",
            "steady_state_watch",
            "drift_issue_open",
            "remediation_reentry_required",
            "executive_review_required",
        ],
    }

    summary = {
        "pack_id": PACK_ID,
        "source_of_truth_commit": actual_head,
        "previous_governance_state": "clinic_wave_steady_state_admission_active",
        "new_governance_state": "multi_clinic_steady_state_governance_active",
        "portfolio_clinic_count": len(clinics),
        "operating_mode": "portfolio_governed_multi_clinic_steady_state",
    }

    validations = [
        ("baseline_commit_match", actual_head == EXPECTED_BASELINE),
        ("five_steady_state_governance_docs_present", len(docs) == 5),
        ("five_clinics_in_portfolio_scope", len(clinics) == 5),
        ("eight_cross_clinic_controls_defined", len(control_posture["required_cross_clinic_controls"]) == 8),
        ("eight_review_domains_defined", len(operating_review["required_review_domains"]) == 8),
        ("six_drift_categories_defined", len(drift_governance["drift_categories"]) == 6),
        ("four_governance_responses_defined", len(drift_governance["governance_responses"]) == 4),
        ("eight_reporting_outputs_defined", len(reporting_visibility["required_reporting_outputs"]) == 8),
        ("state_transition_defined", summary["new_governance_state"] == "multi_clinic_steady_state_governance_active"),
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
    write_json(run_dir / "MULTI_CLINIC_STEADY_STATE_REGISTRY.json", {"clinics": clinics})
    write_json(run_dir / "CROSS_CLINIC_CONTROL_POSTURE_MODEL.json", control_posture)
    write_json(run_dir / "PORTFOLIO_OPERATING_REVIEW_MODEL.json", operating_review)
    write_json(run_dir / "DRIFT_AND_REMEDIATION_GOVERNANCE_MODEL.json", drift_governance)
    write_json(run_dir / "STEADY_STATE_EXECUTIVE_VISIBILITY_MODEL.json", reporting_visibility)
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
    print("PETCARE-MULTI-CLINIC-STEADY-STATE-GOVERNANCE committed state target: multi_clinic_steady_state_governance_active")
    print("Next recommended state: executive_portfolio_steady_state_visibility")


if __name__ == "__main__":
    main()
