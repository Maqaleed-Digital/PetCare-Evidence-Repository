#!/bin/bash
set -e

TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
RUN_DIR="petcare_execution/EVIDENCE/PETCARE-PH6-HOTFIX-ACCESS-UI/$TIMESTAMP"

mkdir -p "$RUN_DIR"

echo "PH6 HOTFIX ACCESS + UI" > "$RUN_DIR/summary.txt"

echo "Expected checks:" >> "$RUN_DIR/summary.txt"
echo "- public route loads" >> "$RUN_DIR/summary.txt"
echo "- unauthorized page loads" >> "$RUN_DIR/summary.txt"
echo "- protected route remains protected" >> "$RUN_DIR/summary.txt"
echo "- polished UI deployed" >> "$RUN_DIR/summary.txt"

echo "Collect route checks" >> "$RUN_DIR/summary.txt"

curl -I https://myveticare.com > "$RUN_DIR/root_headers.txt" || true
curl -I https://myveticare.com/unauthorized > "$RUN_DIR/unauthorized_headers.txt" || true
curl -I https://myveticare.com/signin > "$RUN_DIR/signin_headers.txt" || true
curl -I https://myveticare.com/onboarding > "$RUN_DIR/onboarding_headers.txt" || true

cd "$RUN_DIR"
find . -type f -exec shasum -a 256 {} \; > MANIFEST.sha256

echo "RUN COMPLETE" >> summary.txt
