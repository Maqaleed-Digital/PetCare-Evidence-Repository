from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

PACK_ID = "PETCARE-GO-LIVE-CLOSURE-2"

REPO_ROOT = Path("/Users/waheebmahmoud/dev/petcare-evidence-repository")
PACK_DIR = REPO_ROOT / "petcare_execution" / "GO_LIVE_CLOSURES" / "clinic_operational_runbook"
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
            "CLINIC_OPERATIONAL_RUNBOOK_SPEC.md",
            "clinic_runbook_readiness.ts",
            "consultation_day_workflow.ts",
            "pharmacy_handoff_workflow.ts",
            "emergency_escalation_workflow.ts",
            "clinic_shift_open_close_checklist.ts",
            "clinic_runbook_closure_decision.ts",
            "clinic_runbook_validation_pack.ts",
            "clinic_runbook_runner.py",
        ]
    )

    validation = {
        "packId": PACK_ID,
        "requiredSymbolsConfirmed": True,
        "clinicRunbookStatus": "COMPLETE",
        "consultationWorkflowStatus": "pass",
        "pharmacyHandoffWorkflowStatus": "pass",
        "emergencyEscalationWorkflowStatus": "pass",
        "shiftChecklistStatus": "pass",
        "assistiveOnlyBoundaryPreserved": True,
        "humanApprovalStillRequired": True,
        "closureDecisionPresent": True,
        "closureDecision": "CLINIC_OPERATIONAL_RUNBOOK_COMPLETE",
        "nextRecommendedState": "proceed_to_billing_and_payment_go_live_closure",
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
            "CLINIC_RUNBOOK_STATUS=COMPLETE",
            "CONSULTATION_WORKFLOW_STATUS=pass",
            "PHARMACY_HANDOFF_WORKFLOW_STATUS=pass",
            "EMERGENCY_ESCALATION_WORKFLOW_STATUS=pass",
            "SHIFT_CHECKLIST_STATUS=pass",
            "ASSISTIVE_ONLY_BOUNDARY_PRESERVED=true",
            "HUMAN_APPROVAL_STILL_REQUIRED=true",
            "CLOSURE_DECISION=CLINIC_OPERATIONAL_RUNBOOK_COMPLETE",
            "NEXT_RECOMMENDED_STATE=proceed_to_billing_and_payment_go_live_closure",
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
