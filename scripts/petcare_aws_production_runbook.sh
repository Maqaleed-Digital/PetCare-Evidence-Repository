#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/Users/waheebmahmoud/dev/petcare-evidence-repository"
PACK_ID="PETCARE-AWS-PRODUCTION-RUNBOOK-EXECUTION"
UTC_NOW="$(date -u +"%Y%m%dT%H%M%SZ")"

EVIDENCE_DIR="$REPO_ROOT/petcare_execution/EVIDENCE/$PACK_ID/$UTC_NOW"
mkdir -p "$EVIDENCE_DIR"

echo "PACK_ID=$PACK_ID" > "$EVIDENCE_DIR/ACTIVITY_LOG.txt"
echo "HEAD=$(git -C "$REPO_ROOT" rev-parse HEAD)" >> "$EVIDENCE_DIR/ACTIVITY_LOG.txt"

find "$REPO_ROOT/petcare_execution/AWS_PRODUCTION_RUNBOOK" -type f | sort > "$EVIDENCE_DIR/FILE_LIST.txt"

: > "$EVIDENCE_DIR/SHA256SUMS.txt"
while IFS= read -r f; do
  shasum -a 256 "$f" >> "$EVIDENCE_DIR/SHA256SUMS.txt"
done < "$EVIDENCE_DIR/FILE_LIST.txt"

cat > "$EVIDENCE_DIR/MANIFEST.json" <<MANIFEST
{
 "pack_id":"$PACK_ID",
 "generated_at":"$UTC_NOW"
}
MANIFEST

echo "$EVIDENCE_DIR"
