#!/usr/bin/env bash
set -euo pipefail

PHASE="PETCARE-PH67-CLOSURE"
TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PHASE}"
OUT="${OUT_ROOT}/${TS_UTC}"

mkdir -p "${OUT}/logs" "${OUT}/snapshots"

echo "=============================================="
echo "PetCare PH67 CLOSURE PACK"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "=============================================="

need=(
  "FND/VERIFICATION_INDEX.json"
  "FND/VERIFICATION_INDEX.sha256"
  "scripts/petcare_verification_index_generate.py"
  "scripts/petcare_verification_index_verify.py"
  "scripts/petcare_verification_index_sidecar_write.sh"
  "scripts/petcare_verification_index_sidecar_guard.sh"
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
echo "=== STEP 1: GENERATE (WRITE) + SIDE-CAR WRITE ==="
python3 "${REPO_ROOT}/scripts/petcare_verification_index_generate.py" --write --ts_utc "${TS_UTC}" \
  | tee "${OUT}/logs/index_generate_write.log"
bash "${REPO_ROOT}/scripts/petcare_verification_index_sidecar_write.sh" \
  | tee "${OUT}/logs/index_sidecar_write.log"

echo ""
echo "=== STEP 2: SIDE-CAR GUARD (MUST PASS) ==="
bash "${REPO_ROOT}/scripts/petcare_verification_index_sidecar_guard.sh" \
  | tee "${OUT}/logs/index_sidecar_guard.log"

echo ""
echo "=== STEP 3: VERIFY REAL INDEX (MUST rc=0) ==="
python3 "${REPO_ROOT}/scripts/petcare_verification_index_verify.py" --index "${REPO_ROOT}/FND/VERIFICATION_INDEX.json" \
  | tee "${OUT}/logs/index_verify.log"

echo ""
echo "=== STEP 4: CI GATES (MUST PASS) ==="
bash "${REPO_ROOT}/scripts/petcare_ci_gates.sh" \
  | tee "${OUT}/logs/ci_gates.log"

echo ""
echo "=== SNAPSHOT CONTROL FILES ==="
snap=(
  "FND/VERIFICATION_INDEX.json"
  "FND/VERIFICATION_INDEX.sha256"
  "scripts/petcare_verification_index_generate.py"
  "scripts/petcare_verification_index_verify.py"
  "scripts/petcare_verification_index_sidecar_write.sh"
  "scripts/petcare_verification_index_sidecar_guard.sh"
  "scripts/petcare_ci_gates.sh"
  "scripts/petcare_ph67_closure_pack.sh"
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
