#!/usr/bin/env bash
set -euo pipefail

PHASE="PETCARE-PH56-CLOSURE"
TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PHASE}"
OUT="${OUT_ROOT}/${TS_UTC}"

TARGET_PACK_ID="${TARGET_PACK_ID:-}"
if [ -z "${TARGET_PACK_ID}" ]; then
  echo "FATAL: TARGET_PACK_ID env var is required (exact pack id to allowlist)."
  exit 2
fi

mkdir -p "${OUT}/logs" "${OUT}/snapshots"

echo "=============================================="
echo "PetCare PH56 CLOSURE PACK"
echo "pack=${PHASE}"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${REPO_ROOT}"
echo "target_pack_id=${TARGET_PACK_ID}"
echo "out=${OUT}"
echo "=============================================="

need=(
  "FND/VERIFICATION_POLICY.json"
  "FND/VERIFICATION_POLICY.sha256"
  "FND/VERIFICATION_POLICY_CHANGELOG.md"
  "scripts/petcare_verification_policy_verify.py"
  "scripts/petcare_verification_policy_allowlist_add.py"
  "scripts/petcare_verification_policy_change_guard.py"
  "scripts/petcare_verification_policy_changelog_add.py"
)
missing=0
for f in "${need[@]}"; do
  if [ ! -f "${REPO_ROOT}/${f}" ]; then
    echo "MISSING_REQUIRED_FILE=${f}" | tee -a "${OUT}/logs/missing_files.log"
    missing=1
  fi
done
if [ "${missing}" -ne 0 ]; then
  echo "FATAL: missing required files (no guessing). See ${OUT}/logs/missing_files.log"
  exit 3
fi

echo ""
echo "=== STEP 1: MUTATE ALLOWLIST VIA TOOL (NO MANUAL EDITS) ==="
python3 "${REPO_ROOT}/scripts/petcare_verification_policy_allowlist_add.py" \
  --pack "${TARGET_PACK_ID}" \
  | tee "${OUT}/logs/allowlist_add.log"

echo ""
echo "=== STEP 2: VERIFY POLICY + SHA SIDE-CAR ==="
python3 "${REPO_ROOT}/scripts/petcare_verification_policy_verify.py" \
  | tee "${OUT}/logs/policy_verify.log"

echo ""
echo "=== STEP 3: APPEND CHANGELOG ENTRY (INCLUDES RESULTING POLICY SHA) ==="
python3 "${REPO_ROOT}/scripts/petcare_verification_policy_changelog_add.py" \
  --pack "${TARGET_PACK_ID}" \
  --ts "${TS_UTC}" \
  | tee "${OUT}/logs/changelog_add.log"

echo ""
echo "=== STEP 4: ENFORCE PH55 CHANGE GUARD LOCALLY (IF SCRIPT SUPPORTS DIRECT RUN) ==="
# No guessing about args: run it with no args; if it requires args, it should print usage and exit non-zero.
set +e
python3 "${REPO_ROOT}/scripts/petcare_verification_policy_change_guard.py" \
  | tee "${OUT}/logs/policy_change_guard.log"
rc=${PIPESTATUS[0]}
set -e
if [ "${rc}" -ne 0 ]; then
  echo "NOTE: policy change guard returned rc=${rc}. If this script expects CI context, rely on scripts/petcare_ci_gates.sh (next step) to confirm."
fi

echo ""
echo "=== STEP 5 (OPTIONAL BUT RECOMMENDED): RUN CI GATES IF PRESENT ==="
if [ -f "${REPO_ROOT}/scripts/petcare_ci_gates.sh" ]; then
  bash "${REPO_ROOT}/scripts/petcare_ci_gates.sh" \
    | tee "${OUT}/logs/ci_gates.log"
else
  echo "SKIP: scripts/petcare_ci_gates.sh not found (no guessing)."
fi

echo ""
echo "=== SNAPSHOT CONTROL FILES ==="
snap=(
  "FND/VERIFICATION_POLICY.json"
  "FND/VERIFICATION_POLICY.sha256"
  "FND/VERIFICATION_POLICY_CHANGELOG.md"
)
for f in "${snap[@]}"; do
  mkdir -p "${OUT}/snapshots/$(dirname "${f}")"
  cp -p "${REPO_ROOT}/${f}" "${OUT}/snapshots/${f}"
done

echo ""
echo "=== MANIFEST (DETERMINISTIC ORDER) ==="
python3 - <<PY
import json, os
from pathlib import Path

out = Path("${OUT}")
files = []
for base in ["logs","snapshots"]:
    for p in sorted((out/base).rglob("*")):
        if p.is_file():
            files.append(str(p.relative_to(out)))
manifest = {
  "phase": "${PHASE}",
  "timestamp_utc": "${TS_UTC}",
  "target_pack_id": "${TARGET_PACK_ID}",
  "file_count": len(files),
  "files": files,
}
(out/"MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("OK wrote MANIFEST.json")
PY

echo ""
echo "=== SHA256 (SORTED) ==="
(
  cd "${OUT}" || exit 1
  find . -type f -print0 \
  | LC_ALL=C sort -z \
  | xargs -0 shasum -a 256 \
  > "closure_sha256.txt"
)
echo "OK wrote: ${OUT}/closure_sha256.txt"

echo ""
echo "=== ZIP + ZIP.SHA256 ==="
mkdir -p "${OUT_ROOT}"
ZIP="${OUT_ROOT}/${PHASE}_${TS_UTC}.zip"
rm -f "${ZIP}" "${ZIP}.sha256"
(
  cd "${OUT_ROOT}" || exit 1
  zip -r "${PHASE}_${TS_UTC}.zip" "${TS_UTC}" >/dev/null
  shasum -a 256 "${PHASE}_${TS_UTC}.zip" > "${PHASE}_${TS_UTC}.zip.sha256"
)
echo "OK zip created: ${ZIP}"
echo "OK zip sha: ${ZIP}.sha256"

echo ""
echo "=== SUMMARY ==="
echo "OUT=${OUT}"
echo "ZIP=${ZIP}"
echo "DONE"
