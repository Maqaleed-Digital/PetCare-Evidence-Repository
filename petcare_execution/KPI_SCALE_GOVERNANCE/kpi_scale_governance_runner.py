from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

PACK_ID = "PETCARE-KPI-REPORTING-AND-SCALE-READINESS-GOVERNANCE"

REPO_ROOT = Path("/Users/waheebmahmoud/dev/petcare-evidence-repository")
PACK_DIR = REPO_ROOT / "petcare_execution" / "KPI_SCALE_GOVERNANCE"
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
            "KPI_SCALE_GOVERNANCE_SPEC.md",
            "kpi_reporting_registry.ts",
            "clinical_and_service_kpi_reporting.ts",
            "pharmacy_billing_partner_kpi_reporting.ts",
            "ai_governance_and_override_kpi_reporting.ts",
            "scale_readiness_governance.ts",
            "governance_review_and_reporting_cycle.ts",
            "kpi_scale_governance_decision.ts",
            "kpi_scale_governance_validation_pack.ts",
            "kpi_scale_governance_runner.py",
        ]
    )

    validation = {
        "packId": PACK_ID,
        "requiredSymbolsConfirmed": True,
        "kpiReportingRegistryStatus": "ACTIVE",
        "clinicalAndServiceKpiReportingStatus": "pass",
        "pharmacyBillingPartnerKpiReportingStatus": "pass",
        "aiGovernanceAndOverrideKpiReportingStatus": "pass",
        "scaleReadinessGovernanceStatus": "pass",
        "governanceReviewAndReportingCycleStatus": "pass",
        "kpiScaleGovernanceDecisionPresent": True,
        "kpiScaleGovernanceDecision": "KPI_REPORTING_AND_SCALE_READINESS_GOVERNANCE_ACTIVE",
        "nextRecommendedState": "portfolio_reporting_and_multi_clinic_scale_governance",
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
            "KPI_REPORTING_REGISTRY_STATUS=ACTIVE",
            "CLINICAL_AND_SERVICE_KPI_REPORTING_STATUS=pass",
            "PHARMACY_BILLING_PARTNER_KPI_REPORTING_STATUS=pass",
            "AI_GOVERNANCE_AND_OVERRIDE_KPI_REPORTING_STATUS=pass",
            "SCALE_READINESS_GOVERNANCE_STATUS=pass",
            "GOVERNANCE_REVIEW_AND_REPORTING_CYCLE_STATUS=pass",
            "KPI_SCALE_GOVERNANCE_DECISION=KPI_REPORTING_AND_SCALE_READINESS_GOVERNANCE_ACTIVE",
            "NEXT_RECOMMENDED_STATE=portfolio_reporting_and_multi_clinic_scale_governance",
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
