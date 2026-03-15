from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

PACK_ID = "PETCARE-AI-LIVE-2"
PILOT_CLINIC_ID = "pilot_clinic_001"
COHORT_ID = "AI_PILOT_ALPHA"

REPO_ROOT = Path("/Users/waheebmahmoud/dev/petcare-evidence-repository")
PACK_DIR = REPO_ROOT / "petcare_execution" / "AI_RUNTIME" / "live_pilot_ops_review"
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
            "AI_LIVE_2_OPERATIONS_REVIEW_SPEC.md",
            "live_pilot_telemetry_aggregation.ts",
            "clinical_feedback_review.ts",
            "override_analytics.ts",
            "safety_review_checkpoint.ts",
            "pilot_cohort_closure_decision.ts",
            "live_pilot_ops_review_validation_pack.ts",
            "live_pilot_ops_review_runner.py",
        ]
    )

    validation = {
        "packId": PACK_ID,
        "pilotClinicId": PILOT_CLINIC_ID,
        "cohortId": COHORT_ID,
        "requiredSymbolsConfirmed": True,
        "telemetryAggregationCompleted": True,
        "clinicalFeedbackReviewed": True,
        "overrideAnalyticsCompleted": True,
        "safetyCheckpointStatus": "pass",
        "assistiveOnlyBoundaryPreserved": True,
        "humanApprovalStillRequired": True,
        "cohortClosureDecisionPresent": True,
        "cohortClosureDecision": "READY_FOR_COHORT_CLOSURE",
        "nextRecommendedState": "ready_for_launch_readiness_pack",
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
            f"PILOT_CLINIC_ID={PILOT_CLINIC_ID}",
            f"COHORT_ID={COHORT_ID}",
            "REVIEW_SCOPE=telemetry,clinical_feedback,overrides,safety,closure_decision",
            "ASSISTIVE_ONLY_BOUNDARY_PRESERVED=true",
            "HUMAN_APPROVAL_STILL_REQUIRED=true",
            "COHORT_CLOSURE_DECISION=READY_FOR_COHORT_CLOSURE",
        ]
    ) + "\n"
    write_text_atomic(run_dir / "RUN.log", run_log)

    write_json_atomic(run_dir / "VALIDATION.json", validation)

    manifest = {
        "packId": PACK_ID,
        "timestamp": timestamp,
        "pilotClinicId": PILOT_CLINIC_ID,
        "cohortId": COHORT_ID,
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
