#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/Users/waheebmahmoud/dev/petcare-evidence-repository"
PACK_ID="PETCARE-PRODUCTION-INFRASTRUCTURE-ACTIVATION"
UTC_NOW="$(date -u +"%Y%m%dT%H%M%SZ")"
EVIDENCE_DIR="$REPO_ROOT/petcare_execution/EVIDENCE/$PACK_ID/$UTC_NOW"

mkdir -p "$EVIDENCE_DIR"

echo "PACK_ID=$PACK_ID" > "$EVIDENCE_DIR/ACTIVITY_LOG.txt"
echo "UTC_NOW=$UTC_NOW" >> "$EVIDENCE_DIR/ACTIVITY_LOG.txt"
echo "REPO_ROOT=$REPO_ROOT" >> "$EVIDENCE_DIR/ACTIVITY_LOG.txt"
echo "HEAD=$(git -C "$REPO_ROOT" rev-parse HEAD)" >> "$EVIDENCE_DIR/ACTIVITY_LOG.txt"

find "$REPO_ROOT/petcare_execution/PRODUCTION_INFRASTRUCTURE_ACTIVATION" -type f | sort > "$EVIDENCE_DIR/FILE_LIST.txt"

: > "$EVIDENCE_DIR/SHA256SUMS.txt"
while IFS= read -r file_path; do
  shasum -a 256 "$file_path" >> "$EVIDENCE_DIR/SHA256SUMS.txt"
done < "$EVIDENCE_DIR/FILE_LIST.txt"

cat > "$EVIDENCE_DIR/MANIFEST.json" <<MANIFEST
{
  "pack_id": "$PACK_ID",
  "generated_at_utc": "$UTC_NOW",
  "source_of_truth_before_commit": "$(git -C "$REPO_ROOT" rev-parse HEAD)",
  "artifact_root": "$REPO_ROOT/petcare_execution/PRODUCTION_INFRASTRUCTURE_ACTIVATION",
  "evidence_dir": "$EVIDENCE_DIR"
}
MANIFEST

echo "EVIDENCE_DIR=$EVIDENCE_DIR"
