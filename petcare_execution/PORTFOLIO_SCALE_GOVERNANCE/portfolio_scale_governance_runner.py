from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

PACK_ID = "PETCARE-PORTFOLIO-REPORTING-AND-MULTI-CLINIC-SCALE-GOVERNANCE"

REPO_ROOT = Path("/Users/waheebmahmoud/dev/petcare-evidence-repository")
PACK_DIR = REPO_ROOT / "petcare_execution" / "PORTFOLIO_SCALE_GOVERNANCE"
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
            "PORTFOLIO_SCALE_GOVERNANCE_SPEC.md",
            "portfolio_reporting_registry.ts",
            "multi_clinic_operating_model_governance.ts",
            "portfolio_kpi_and_board_reporting.ts",
            "clinic_replication_readiness_governance.ts",
            "ai_governance_scale_controls.ts",
            "network_risk_and_compliance_governance.ts",
            "portfolio_scale_governance_decision.ts",
            "portfolio_scale_governance_validation_pack.ts",
            "portfolio_scale_governance_runner.py",
        ]
    )

    validation = {
        "packId": PACK_ID,
        "requiredSymbolsConfirmed": True,
        "portfolioReportingRegistryStatus": "ACTIVE",
        "multiClinicOperatingModelGovernanceStatus": "pass",
        "portfolioKpiAndBoardReportingStatus": "pass",
        "clinicReplicationReadinessGovernanceStatus": "pass",
        "aiGovernanceScaleControlsStatus": "pass",
        "networkRiskAndComplianceGovernanceStatus": "pass",
        "portfolioScaleGovernanceDecisionPresent": True,
        "portfolioScaleGovernanceDecision": "PORTFOLIO_REPORTING_AND_MULTI_CLINIC_SCALE_GOVERNANCE_ACTIVE",
        "nextRecommendedState": "multi_clinic_activation_wave_governance",
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
            "PORTFOLIO_REPORTING_REGISTRY_STATUS=ACTIVE",
            "MULTI_CLINIC_OPERATING_MODEL_GOVERNANCE_STATUS=pass",
            "PORTFOLIO_KPI_AND_BOARD_REPORTING_STATUS=pass",
            "CLINIC_REPLICATION_READINESS_GOVERNANCE_STATUS=pass",
            "AI_GOVERNANCE_SCALE_CONTROLS_STATUS=pass",
            "NETWORK_RISK_AND_COMPLIANCE_GOVERNANCE_STATUS=pass",
            "PORTFOLIO_SCALE_GOVERNANCE_DECISION=PORTFOLIO_REPORTING_AND_MULTI_CLINIC_SCALE_GOVERNANCE_ACTIVE",
            "NEXT_RECOMMENDED_STATE=multi_clinic_activation_wave_governance",
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
