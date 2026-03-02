#!/usr/bin/env bash
set -euo pipefail

PHASE="PETCARE-PH63-CLOSURE"
TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PHASE}"
OUT="${OUT_ROOT}/${TS_UTC}"

mkdir -p "${OUT}/logs" "${OUT}/snapshots"

echo "=============================================="
echo "PetCare PH63 CLOSURE PACK"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "=============================================="

need=(
  "FND/VERIFICATION_POLICY.json"
  "FND/VERIFICATION_POLICY.sha256"
  "FND/VERIFICATION_POLICY_CHANGELOG.md"
  "FND/VERIFICATION_INDEX.json"
  "scripts/petcare_verification_policy_verify.py"
  "scripts/petcare_verification_policy_changelog_add.py"
  "scripts/petcare_verification_index_verify.py"
  "scripts/petcare_verification_index_patch_quorum.py"
  "scripts/petcare_ci_gates.sh"
)
missing=0
for f in "${need[@]}"; do
  if [ ! -f "${REPO_ROOT}/${f}" ]; then
    echo "MISSING_REQUIRED_FILE=${f}" | tee -a "${OUT}/logs/missing_files.log"
    missing=1
  fi
done
if [ "${missing}" -ne 0 ]; then
  echo "FATAL: missing required files. Stop (no guessing)."
  exit 3
fi

echo ""
echo "=== STEP 1: POLICY VERIFY ==="
python3 "${REPO_ROOT}/scripts/petcare_verification_policy_verify.py" \
  | tee "${OUT}/logs/policy_verify.log"

echo ""
echo "=== STEP 2: REAL INDEX VERIFY (EXPECT rc=135 BEFORE PATCH) ==="
set +e
python3 "${REPO_ROOT}/scripts/petcare_verification_index_verify.py" \
  --index "${REPO_ROOT}/FND/VERIFICATION_INDEX.json" \
  | tee "${OUT}/logs/index_verify_before.log"
rc_before=${PIPESTATUS[0]}
set -e
echo "RC_BEFORE=${rc_before}" | tee -a "${OUT}/logs/index_verify_before.log"
if [ "${rc_before}" -ne 135 ] && [ "${rc_before}" -ne 0 ]; then
  echo "FATAL: unexpected rc_before=${rc_before}. Expected 135 or 0." | tee -a "${OUT}/logs/index_verify_before.log"
  exit 10
fi

echo ""
echo "=== STEP 3: PATCH REAL INDEX TO MEET QUORUM (DETERMINISTIC) ==="
python3 "${REPO_ROOT}/scripts/petcare_verification_index_patch_quorum.py" \
  --ts_utc "${TS_UTC}" \
  | tee "${OUT}/logs/index_patch_quorum.log"

echo ""
echo "=== STEP 4: REAL INDEX VERIFY AFTER PATCH (MUST rc=0) ==="
python3 "${REPO_ROOT}/scripts/petcare_verification_index_verify.py" \
  --index "${REPO_ROOT}/FND/VERIFICATION_INDEX.json" \
  | tee "${OUT}/logs/index_verify_after.log"

echo ""
echo "=== STEP 5: CHANGELOG APPEND (RECORD POLICY SHA) ==="
python3 "${REPO_ROOT}/scripts/petcare_verification_policy_changelog_add.py" \
  --pack "PH63-REAL-INDEX-QUORUM-MET" \
  --ts "${TS_UTC}" \
  | tee "${OUT}/logs/changelog_add.log"

echo ""
echo "=== STEP 6: CI GATES ==="
bash "${REPO_ROOT}/scripts/petcare_ci_gates.sh" \
  | tee "${OUT}/logs/ci_gates.log"

echo ""
echo "=== SNAPSHOT CONTROL FILES ==="
snap=(
  "FND/VERIFICATION_POLICY.json"
  "FND/VERIFICATION_POLICY.sha256"
  "FND/VERIFICATION_POLICY_CHANGELOG.md"
  "FND/VERIFICATION_INDEX.json"
  "scripts/petcare_verification_index_patch_quorum.py"
  "scripts/petcare_verification_index_verify.py"
  "scripts/petcare_ph63_closure_pack.sh"
)
for f in "${snap[@]}"; do
  mkdir -p "${OUT}/snapshots/$(dirname "${f}")"
  cp -p "${REPO_ROOT}/${f}" "${OUT}/snapshots/${f}"
done

echo ""
echo "=== MANIFEST ==="
python3 - <<PY
import json
from pathlib import Path
out=Path("${OUT}")
files=[str(p.relative_to(out)) for p in sorted(out.rglob("*")) if p.is_file()]
m={"phase":"${PHASE}","timestamp_utc":"${TS_UTC}","file_count":len(files),"files":files}
(out/"MANIFEST.json").write_text(json.dumps(m, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
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

echo ""
echo "DONE"
echo "OUT=${OUT}"
echo "ZIP=${ZIP}"
