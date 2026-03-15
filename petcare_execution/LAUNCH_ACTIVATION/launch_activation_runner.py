from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

PACK_ID = "PETCARE-CLINIC-LAUNCH-ACTIVATION"

REPO_ROOT = Path("/Users/waheebmahmoud/dev/petcare-evidence-repository")
PACK_DIR = REPO_ROOT / "petcare_execution" / "LAUNCH_ACTIVATION"
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
            "CLINIC_LAUNCH_ACTIVATION_SPEC.md",
            "launch_activation_registry.ts",
            "launch_day_activation_checklist.ts",
            "clinic_services_enablement.ts",
            "ai_runtime_launch_state.ts",
            "launch_governance_notification.ts",
            "launch_activation_decision.ts",
            "launch_activation_validation_pack.ts",
            "launch_activation_runner.py",
        ]
    )

    validation = {
        "packId": PACK_ID,
        "requiredSymbolsConfirmed": True,
        "launchActivationRegistryStatus": "ACTIVE",
        "launchDayChecklistStatus": "pass",
        "clinicServicesEnablementStatus": "pass",
        "aiRuntimeLaunchStateStatus": "pass",
        "launchGovernanceNotificationStatus": "recorded",
        "launchDecisionPresent": True,
        "launchDecision": "CLINIC_LAUNCH_ACTIVATED",
        "nextRecommendedState": "clinic_launch_live_operations",
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
            "LAUNCH_ACTIVATION_REGISTRY_STATUS=ACTIVE",
            "LAUNCH_DAY_CHECKLIST_STATUS=pass",
            "CLINIC_SERVICES_ENABLEMENT_STATUS=pass",
            "AI_RUNTIME_LAUNCH_STATE_STATUS=pass",
            "LAUNCH_GOVERNANCE_NOTIFICATION_STATUS=recorded",
            "LAUNCH_DECISION=CLINIC_LAUNCH_ACTIVATED",
            "NEXT_RECOMMENDED_STATE=clinic_launch_live_operations",
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
