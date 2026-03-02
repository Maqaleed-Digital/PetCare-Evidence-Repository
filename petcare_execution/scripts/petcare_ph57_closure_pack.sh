#!/usr/bin/env bash
set -euo pipefail

PHASE="PETCARE-PH57-CLOSURE"
TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PHASE}"
OUT="${OUT_ROOT}/${TS_UTC}"

TARGET_META="PETCARE-PH44B-CLOSURE"

mkdir -p "${OUT}/logs"

echo "=============================================="
echo "PetCare PH57 CLOSURE PACK"
echo "timestamp_utc=${TS_UTC}"
echo "meta_verifier=${TARGET_META}"
echo "=============================================="

echo ""
echo "=== STEP 1: POLICY VERIFY ==="
python3 "${REPO_ROOT}/scripts/petcare_verification_policy_verify.py" \
  | tee "${OUT}/logs/policy_verify.log"

echo ""
echo "=== STEP 2: RUN VERIFICATION INDEX (LIVE CHAIN TEST) ==="
python3 "${REPO_ROOT}/scripts/petcare_verification_index_verify.py" \
  | tee "${OUT}/logs/meta_chain_verify.log"

echo ""
echo "=== SNAPSHOT CONTROL FILES ==="
mkdir -p "${OUT}/snapshots/FND"
cp -p "${REPO_ROOT}/FND/VERIFICATION_POLICY.json" \
      "${OUT}/snapshots/FND/"
cp -p "${REPO_ROOT}/FND/VERIFICATION_POLICY.sha256" \
      "${OUT}/snapshots/FND/"

echo ""
echo "=== MANIFEST ==="
python3 - <<PY
import json, os
from pathlib import Path

out = Path("${OUT}")
files = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())

manifest = {
  "phase": "${PHASE}",
  "timestamp_utc": "${TS_UTC}",
  "meta_verifier": "${TARGET_META}",
  "file_count": len(files),
  "files": files,
}

(out/"MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
print("OK wrote MANIFEST.json")
PY

echo ""
echo "=== SHA256 ==="
(
  cd "${OUT}" || exit 1
  find . -type f -print0 \
  | LC_ALL=C sort -z \
  | xargs -0 shasum -a 256 \
  > "closure_sha256.txt"
)

echo ""
echo "=== ZIP ==="
mkdir -p "${OUT_ROOT}"
ZIP="${OUT_ROOT}/${PHASE}_${TS_UTC}.zip"
rm -f "${ZIP}" "${ZIP}.sha256"
(
  cd "${OUT_ROOT}" || exit 1
  zip -r "${PHASE}_${TS_UTC}.zip" "${TS_UTC}" >/dev/null
  shasum -a 256 "${PHASE}_${TS_UTC}.zip" > "${PHASE}_${TS_UTC}.zip.sha256"
)

echo ""
echo "DONE"
echo "ZIP=${ZIP}"
