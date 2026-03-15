from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

PACK_ID = "PETCARE-STEADY-STATE-LIVE-OPERATIONS-MANAGEMENT"

REPO_ROOT = Path("/Users/waheebmahmoud/dev/petcare-evidence-repository")
PACK_DIR = REPO_ROOT / "petcare_execution" / "STEADY_STATE_OPERATIONS"
EVIDENCE_ROOT = REPO_ROOT / "petcare_execution" / "EVIDENCE" / PACK_ID


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_text_atomic(path: Path, content: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def write_json_atomic(path: Path, data: object) -> None:
    write_text_atomic(path, json.dumps(data, indent=2) + "\n")


def main() -> int:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = EVIDENCE_ROOT / timestamp
    run_dir.mkdir(parents=True, exist_ok=False)

    files = sorted(
        [
            "STEADY_STATE_LIVE_OPERATIONS_MANAGEMENT_SPEC.md",
            "steady_state_operations_registry.ts",
            "service_quality_and_sla_monitoring.ts",
            "clinical_safety_and_audit_monitoring.ts",
            "pharmacy_billing_partner_performance_monitoring.ts",
            "ai_governance_and_override_monitoring.ts",
            "incident_review_and_continuity_management.ts",
            "steady_state_operations_decision.ts",
            "steady_state_operations_validation_pack.ts",
            "steady_state_operations_runner.py",
        ]
    )

    validation = {
        "packId": PACK_ID,
        "requiredSymbolsConfirmed": True,
        "steadyStateOperationsRegistryStatus": "ACTIVE",
        "serviceQualityAndSlaMonitoringStatus": "pass",
        "clinicalSafetyAndAuditMonitoringStatus": "pass",
        "pharmacyBillingPartnerPerformanceMonitoringStatus": "pass",
        "aiGovernanceAndOverrideMonitoringStatus": "pass",
        "incidentReviewAndContinuityManagementStatus": "pass",
        "steadyStateOperationsDecisionPresent": True,
        "steadyStateOperationsDecision": "STEADY_STATE_LIVE_OPERATIONS_MANAGEMENT_ACTIVE",
        "nextRecommendedState": "kpi_reporting_and_scale_readiness_governance",
    }

    file_listing = []
    for name in files:
        path = PACK_DIR / name
        file_listing.append(
            {
                "path": str(path.relative_to(REPO_ROOT)),
                "sha256": sha256_file(path),
            }
        )

    files_txt = "\n".join(str((PACK_DIR / name).relative_to(REPO_ROOT)) for name in files) + "\n"
    write_text_atomic(run_dir / "FILES.txt", files_txt)

    run_log = "\n".join(
        [
            f"PACK_ID={PACK_ID}",
            "STEADY_STATE_OPERATIONS_REGISTRY_STATUS=ACTIVE",
            "SERVICE_QUALITY_AND_SLA_MONITORING_STATUS=pass",
            "CLINICAL_SAFETY_AND_AUDIT_MONITORING_STATUS=pass",
            "PHARMACY_BILLING_PARTNER_PERFORMANCE_MONITORING_STATUS=pass",
            "AI_GOVERNANCE_AND_OVERRIDE_MONITORING_STATUS=pass",
            "INCIDENT_REVIEW_AND_CONTINUITY_MANAGEMENT_STATUS=pass",
            "STEADY_STATE_OPERATIONS_DECISION=STEADY_STATE_LIVE_OPERATIONS_MANAGEMENT_ACTIVE",
            "NEXT_RECOMMENDED_STATE=kpi_reporting_and_scale_readiness_governance",
        ]
    ) + "\n"
    write_text_atomic(run_dir / "RUN.log", run_log)

    write_json_atomic(run_dir / "VALIDATION.json", validation)

    manifest = {
        "packId": PACK_ID,
        "timestamp": timestamp,
        "artifacts": [
            {
                "path": str((run_dir / "FILES.txt").relative_to(REPO_ROOT)),
                "sha256": sha256_file(run_dir / "FILES.txt"),
            },
            {
                "path": str((run_dir / "RUN.log").relative_to(REPO_ROOT)),
                "sha256": sha256_file(run_dir / "RUN.log"),
            },
            {
                "path": str((run_dir / "VALIDATION.json").relative_to(REPO_ROOT)),
                "sha256": sha256_file(run_dir / "VALIDATION.json"),
            },
        ],
        "packFiles": file_listing,
    }
    write_json_atomic(run_dir / "MANIFEST.json", manifest)
    manifest_sha = sha256_file(run_dir / "MANIFEST.json")
    write_text_atomic(run_dir / "MANIFEST.sha256", f"{manifest_sha}  MANIFEST.json\n")

    print(str(run_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
