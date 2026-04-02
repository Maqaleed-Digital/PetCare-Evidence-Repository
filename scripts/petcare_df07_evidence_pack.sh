#!/usr/bin/env bash
set -euo pipefail

: "${PETCARE_EVIDENCE_ROOT:?PETCARE_EVIDENCE_ROOT is required}"
: "${PETCARE_RELEASE_COMMIT:?PETCARE_RELEASE_COMMIT is required}"
: "${PETCARE_ARTIFACT_DIGEST:?PETCARE_ARTIFACT_DIGEST is required}"

RUN_TS="$(date -u +%Y%m%dT%H%M%SZ)"
EVIDENCE_DIR="${PETCARE_EVIDENCE_ROOT%/}/PETCARE-PHASE-2-DF07-PROD-GATE-IMPLEMENTATION/${RUN_TS}"
mkdir -p "$EVIDENCE_DIR"

printf '%s\n' "${PETCARE_RELEASE_COMMIT}" > "$EVIDENCE_DIR/release_commit.txt"
printf '%s\n' "${PETCARE_ARTIFACT_DIGEST}" > "$EVIDENCE_DIR/artifact_digest.txt"
printf '%s\n' "${PETCARE_RELEASE_APPROVER:-UNSET}" > "$EVIDENCE_DIR/release_approver.txt"
printf '%s\n' "${PETCARE_DEPLOY_OPERATOR:-UNSET}" > "$EVIDENCE_DIR/deploy_operator.txt"
printf '%s\n' "${PETCARE_ROLLBACK_TARGET:-UNSET}" > "$EVIDENCE_DIR/rollback_target.txt"
printf '%s\n' "${PETCARE_NONPROD_SERVICE_URL:-UNSET}" > "$EVIDENCE_DIR/nonprod_service_url.txt"
printf '%s\n' "${PETCARE_PROD_SERVICE_URL:-UNSET}" > "$EVIDENCE_DIR/prod_service_url.txt"
printf '%s\n' "${PETCARE_CHANGE_RECORD:-UNSET}" > "$EVIDENCE_DIR/change_record.txt"

find "$EVIDENCE_DIR" -maxdepth 1 -type f | sort > "$EVIDENCE_DIR/file_listing.txt"

export EVIDENCE_DIR
python3 - <<'PY'
import hashlib, json, os, pathlib

evidence_dir = pathlib.Path(os.environ["EVIDENCE_DIR"])
files = sorted([p for p in evidence_dir.iterdir() if p.is_file() and p.name not in {"MANIFEST.json", "MANIFEST.sha256"}])

manifest = {
    "pack_id": "PETCARE-PHASE-2-DF07-PROD-GATE-IMPLEMENTATION",
    "run_dir": str(evidence_dir),
    "files": []
}

for p in files:
    manifest["files"].append({
        "name": p.name,
        "sha256": hashlib.sha256(p.read_bytes()).hexdigest()
    })

manifest_path = evidence_dir / "MANIFEST.json"
manifest_path.write_text(json.dumps(manifest, indent=2))
(evidence_dir / "MANIFEST.sha256").write_text(hashlib.sha256(manifest_path.read_bytes()).hexdigest() + "\n")
PY

echo "DF07_EVIDENCE_PACK: PASS"
echo "EVIDENCE_RUN_DIR=${EVIDENCE_DIR}"
