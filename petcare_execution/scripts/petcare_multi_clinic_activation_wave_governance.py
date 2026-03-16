#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path

PACK_ID = "PETCARE-MULTI-CLINIC-ACTIVATION-WAVE-GOVERNANCE"
EXPECTED_BASELINE = "160ab4c5dddb6b23dc16e63f5ee16e8cc452e504"

REPO_ROOT = Path("/Users/waheebmahmoud/dev/petcare-evidence-repository")
DOC_DIR = REPO_ROOT / "petcare_execution" / "GOVERNANCE" / "MULTI_CLINIC_ACTIVATION_WAVE"
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

    run_id = utc_run_id()
    run_dir = EVIDENCE_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    docs = sorted(DOC_DIR.glob("*.md"))
    if len(docs) != 5:
        raise SystemExit(f"STOP: expected 5 governance docs, found {len(docs)}")

    clinic_wave_registry = {
        "baseline_clinic": "CLINIC-LIVE-BASELINE-001",
        "activation_wave": [
            {"clinic_code": "CLINIC-WAVE2-001", "wave": "WAVE_2", "stage": "candidate_registration"},
            {"clinic_code": "CLINIC-WAVE2-002", "wave": "WAVE_2", "stage": "candidate_registration"},
            {"clinic_code": "CLINIC-WAVEN-001", "wave": "WAVE_N", "stage": "candidate_registration"},
            {"clinic_code": "CLINIC-WAVEN-002", "wave": "WAVE_N", "stage": "candidate_registration"},
        ],
    }

    activation_wave_controls = {
        "control_domains": [
            "site_governance",
            "clinical_operations",
            "workforce_readiness",
            "ai_safety_and_hitl_enforcement",
            "reporting_and_evidence",
            "partner_connectivity",
            "escalation_and_incident_routing",
            "hypercare_monitoring",
        ],
        "hard_stop_controls": [
            "missing_human_approval_enforcement",
            "missing_override_capture",
            "missing_escalation_routing",
            "missing_evidence_path",
            "missing_kpi_visibility",
            "unresolved_material_clinical_safety_issue",
        ],
    }

    ai_site_safety_matrix = {
        "assistive_ai_boundary": True,
        "required_controls": [
            "human_in_the_loop_preserved",
            "override_event_logging_per_site",
            "escalation_pathway_per_site",
            "kill_switch_authority_per_site",
            "central_policy_consistency_across_sites",
            "cross_site_comparison_of_override_rates",
            "hypercare_observation_for_newly_activated_sites",
            "portfolio_level_review_of_safety_deviations",
        ],
        "site_variation_allowed": [
            "site_code",
            "local_staffing_roster",
            "local_escalation_contacts",
            "local_operating_windows",
            "clinic_activation_state",
        ],
    }

    partner_network_governance = {
        "partner_categories": [
            "pharmacy_and_medication_fulfillment",
            "diagnostics_and_laboratory",
            "referral_and_emergency",
        ],
        "control_tiers": ["tier_1", "tier_2", "tier_3"],
        "required_reporting": [
            "partner_usage_by_clinic",
            "incident_count_by_partner_category",
            "fallback_activation_frequency",
            "dependency_concentration_view",
        ],
    }

    portfolio_comparison = {
        "baseline_clinic": "CLINIC-LIVE-BASELINE-001",
        "comparison_metrics": [
            "activation_status",
            "hypercare_status",
            "override_event_rate",
            "escalation_event_rate",
            "kpi_capture_completeness",
            "partner_dependency_concentration",
            "staffing_readiness_coverage",
            "ai_safety_attestation_status",
        ],
        "comparison_buckets": [
            "baseline_clinic",
            "newly_activated_clinics",
            "hypercare_clinics",
            "steady_state_clinics",
        ],
    }

    summary = {
        "pack_id": PACK_ID,
        "source_of_truth_commit": actual_head,
        "previous_governance_state": "governed_multi_clinic_ai_controls_active",
        "new_governance_state": "multi_clinic_activation_wave_governance_active",
        "pack_scope": [
            "clinic_replication_governance",
            "activation_wave_controls",
            "multi_site_ai_safety_controls",
            "partner_network_scaling_governance",
            "portfolio_performance_comparison",
        ],
        "wave_admission_model": "controlled_replication",
    }

    validations = [
        ("baseline_commit_match", actual_head == EXPECTED_BASELINE),
        ("five_governance_docs_present", len(docs) == 5),
        ("four_candidate_clinics_defined", len(clinic_wave_registry["activation_wave"]) == 4),
        ("eight_control_domains_defined", len(activation_wave_controls["control_domains"]) == 8),
        ("six_hard_stop_controls_defined", len(activation_wave_controls["hard_stop_controls"]) == 6),
        ("eight_ai_controls_defined", len(ai_site_safety_matrix["required_controls"]) == 8),
        ("three_partner_categories_defined", len(partner_network_governance["partner_categories"]) == 3),
        ("eight_portfolio_metrics_defined", len(portfolio_comparison["comparison_metrics"]) == 8),
        ("state_transition_defined", summary["new_governance_state"] == "multi_clinic_activation_wave_governance_active"),
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
    write_json(run_dir / "CLINIC_WAVE_REGISTRY.json", clinic_wave_registry)
    write_json(run_dir / "ACTIVATION_WAVE_CONTROLS.json", activation_wave_controls)
    write_json(run_dir / "AI_SITE_SAFETY_MATRIX.json", ai_site_safety_matrix)
    write_json(run_dir / "PARTNER_NETWORK_GOVERNANCE.json", partner_network_governance)
    write_json(run_dir / "PORTFOLIO_COMPARISON.json", portfolio_comparison)
    write_json(run_dir / "VALIDATION_REPORT.json", validation_report)

    manifest = {
        "pack_id": PACK_ID,
        "run_id": run_id,
        "source_of_truth_commit": actual_head,
        "generated_at_utc": run_id,
        "files": [],
    }

    for path in sorted(run_dir.iterdir()):
        manifest["files"].append(
            {
                "path": path.name,
                "sha256": sha256_file(path),
            }
        )

    write_json(run_dir / "MANIFEST.json", manifest)
    manifest_sha = hashlib.sha256((run_dir / "MANIFEST.json").read_bytes()).hexdigest()
    (run_dir / "MANIFEST.sha256").write_text(f"{manifest_sha}  MANIFEST.json\n", encoding="utf-8")

    print(f"PACK_ID              : {PACK_ID}")
    print(f"VALIDATION           : OK ({validation_report['assertions_passed']}/{validation_report['assertions_total']} assertions passed)")
    print(f"EVIDENCE_RUN_DIR     : {run_dir.relative_to(REPO_ROOT)}")
    print(f"SOURCE_OF_TRUTH_COMMIT: {actual_head}")
    print("PETCARE-MULTI-CLINIC-ACTIVATION-WAVE-GOVERNANCE committed state target: multi_clinic_activation_wave_governance_active")
    print("Next recommended state: clinic_wave_execution_readiness")


if __name__ == "__main__":
    main()
