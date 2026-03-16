#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path

PACK_ID = "PETCARE-EXECUTIVE-PORTFOLIO-STEADY-STATE-VISIBILITY"
EXPECTED_BASELINE = "173208936a65ed8db0550f8be4850225988ced6d"

REPO_ROOT = Path("/Users/waheebmahmoud/dev/petcare-evidence-repository")
DOC_DIR = REPO_ROOT / "petcare_execution" / "GOVERNANCE" / "EXECUTIVE_PORTFOLIO_STEADY_STATE_VISIBILITY"
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
        raise SystemExit(f"STOP: expected 5 executive visibility docs, found {len(docs)}")

    run_id = utc_run_id()
    run_dir = EVIDENCE_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    clinics = [
        {"clinic_code": "CLINIC-LIVE-BASELINE-001", "executive_state": "steady_state_operational"},
        {"clinic_code": "CLINIC-WAVE2-001", "executive_state": "steady_state_operational"},
        {"clinic_code": "CLINIC-WAVE2-002", "executive_state": "steady_state_operational"},
        {"clinic_code": "CLINIC-WAVEN-001", "executive_state": "steady_state_operational"},
        {"clinic_code": "CLINIC-WAVEN-002", "executive_state": "steady_state_operational"},
    ]

    executive_kpis = {
        "required_executive_kpis": [
            "clinic_count_in_portfolio",
            "steady_state_operational_count",
            "clinics_on_watch_count",
            "open_drift_issue_count",
            "remediation_reentry_count",
            "override_posture_summary",
            "escalation_posture_summary",
            "kpi_completeness_summary",
        ],
        "required_exception_views": [
            "clinics_requiring_executive_review",
            "clinics_with_drift_issues_open",
            "clinics_under_remediation_reentry",
            "clinics_under_watch_posture",
        ],
    }

    comparison_framework = {
        "required_comparison_summary_domains": [
            "steady_state_status_by_clinic",
            "control_posture_by_clinic",
            "override_posture_by_clinic",
            "escalation_posture_by_clinic",
            "kpi_completeness_by_clinic",
            "drift_posture_by_clinic",
            "remediation_posture_by_clinic",
            "comparison_against_baseline_clinic",
        ],
        "required_portfolio_groupings": [
            "baseline_live_clinic",
            "steady_state_operational_clinics",
            "clinics_on_watch",
            "clinics_under_remediation_attention",
        ],
    }

    intervention_attention = {
        "attention_categories": [
            "routine_visibility",
            "watch_visibility",
            "intervention_attention",
            "urgent_portfolio_review",
        ],
        "attention_triggers": [
            "control_posture_issue",
            "drift_issue",
            "remediation_reentry",
            "kpi_completeness_concern",
            "escalation_posture_concern",
            "cross_clinic_comparison_deterioration",
        ],
    }

    executive_reporting = {
        "required_executive_reporting_outputs": [
            "portfolio_clinic_count",
            "steady_state_posture_summary",
            "watch_posture_summary",
            "drift_issue_summary",
            "remediation_reentry_summary",
            "override_posture_summary",
            "escalation_posture_summary",
            "kpi_completeness_summary",
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
        "previous_governance_state": "multi_clinic_steady_state_governance_active",
        "new_governance_state": "executive_portfolio_steady_state_visibility_active",
        "portfolio_clinic_count": len(clinics),
        "executive_visibility_mode": "portfolio_summary_and_exception_visibility",
    }

    validations = [
        ("baseline_commit_match", actual_head == EXPECTED_BASELINE),
        ("five_executive_visibility_docs_present", len(docs) == 5),
        ("five_clinics_in_executive_scope", len(clinics) == 5),
        ("eight_executive_kpis_defined", len(executive_kpis["required_executive_kpis"]) == 8),
        ("four_exception_views_defined", len(executive_kpis["required_exception_views"]) == 4),
        ("eight_comparison_domains_defined", len(comparison_framework["required_comparison_summary_domains"]) == 8),
        ("four_attention_categories_defined", len(intervention_attention["attention_categories"]) == 4),
        ("eight_executive_reporting_outputs_defined", len(executive_reporting["required_executive_reporting_outputs"]) == 8),
        ("state_transition_defined", summary["new_governance_state"] == "executive_portfolio_steady_state_visibility_active"),
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
    write_json(run_dir / "EXECUTIVE_PORTFOLIO_CLINIC_REGISTRY.json", {"clinics": clinics})
    write_json(run_dir / "EXECUTIVE_KPI_AND_EXCEPTION_MODEL.json", executive_kpis)
    write_json(run_dir / "PORTFOLIO_COMPARISON_SUMMARY_MODEL.json", comparison_framework)
    write_json(run_dir / "EXECUTIVE_INTERVENTION_ATTENTION_MODEL.json", intervention_attention)
    write_json(run_dir / "EXECUTIVE_REVIEW_REPORTING_MODEL.json", executive_reporting)
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
    print("PETCARE-EXECUTIVE-PORTFOLIO-STEADY-STATE-VISIBILITY committed state target: executive_portfolio_steady_state_visibility_active")
    print("Next recommended state: executive_portfolio_intervention_governance")


if __name__ == "__main__":
    main()
