#!/bin/bash
set -e

TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
RUN_DIR="petcare_execution/EVIDENCE/PETCARE-PHASE-6-PILOT-ACTIVATION/$TIMESTAMP"

mkdir -p "$RUN_DIR"

echo "PH6 PILOT ACTIVATION RUN" > "$RUN_DIR/summary.txt"

echo "Checking live endpoints..." >> "$RUN_DIR/summary.txt"

curl -s https://myveticare.com >> "$RUN_DIR/web_check.html"
curl -s https://petcare-api-prod-232802712581.me-central2.run.app/health >> "$RUN_DIR/api_health.txt"

echo "Collecting audit samples..." >> "$RUN_DIR/summary.txt"

# Placeholder: real audit pull must be connected to backend logs
echo "audit_sample_placeholder" > "$RUN_DIR/audit_sample.log"

echo "Generating manifest..."

cd "$RUN_DIR"
find . -type f -exec shasum -a 256 {} \; > MANIFEST.sha256

echo "RUN COMPLETE" >> summary.txt
