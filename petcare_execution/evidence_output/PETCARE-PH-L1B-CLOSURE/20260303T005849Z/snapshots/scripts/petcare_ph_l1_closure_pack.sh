#!/usr/bin/env bash
set -euo pipefail

PHASE="PETCARE-PH-L1-CLOSURE"
TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PHASE}"
OUT="${OUT_ROOT}/${TS_UTC}"

mkdir -p "${OUT}/logs"

echo "=== PH-L1 PRODUCTION FREEZE ==="

echo "STEP 1: CI gates"
bash "${REPO_ROOT}/scripts/petcare_ci_gates.sh" | tee "${OUT}/logs/ci_gates.log"

echo "STEP 2: Release integrity"
bash "${REPO_ROOT}/scripts/petcare_release_integrity_check.sh" \
  | tee "${OUT}/logs/release_integrity.log" || true

echo "STEP 3: Git status"
git status -sb | tee "${OUT}/logs/git_status.log"

echo "STEP 4: Verification index"
python3 "${REPO_ROOT}/scripts/petcare_verification_index_verify.py" \
  --index "${REPO_ROOT}/FND/VERIFICATION_INDEX.json" \
  | tee "${OUT}/logs/index_verify.log"

echo "STEP 5: Tag verification"
git describe --tags | tee "${OUT}/logs/tag.log"

echo "=== ZIP ==="
cd "${OUT_ROOT}"
zip -r "${PHASE}_${TS_UTC}.zip" "${TS_UTC}" >/dev/null
shasum -a 256 "${PHASE}_${TS_UTC}.zip" > "${PHASE}_${TS_UTC}.zip.sha256"

echo "DONE"
