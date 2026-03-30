#!/usr/bin/env bash
set -euo pipefail

PHASE="PETCARE-PH-L2-CLOSURE"
TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PHASE}"
OUT="${OUT_ROOT}/${TS_UTC}"

# RTO budget (seconds)
RTO_MAX_SECONDS="${RTO_MAX_SECONDS:-900}"

mkdir -p "${OUT}/logs" "${OUT}/snapshots"

echo "=============================================="
echo "PetCare PH-L2 CLOSURE PACK"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "rto_max_seconds=${RTO_MAX_SECONDS}"
echo "=============================================="

need=(
  "scripts/petcare_backup_create.sh"
  "scripts/petcare_restore_apply.sh"
  "scripts/petcare_ci_gates.sh"
  "scripts/petcare_verification_index_generate.py"
  "scripts/petcare_verification_index_sidecar_write.sh"
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

t0="$(date +%s)"

echo ""
echo "=== STEP 1: BACKUP CREATE ==="
export TS_UTC
export OUT_DIR="${OUT}/backup"
bash "${REPO_ROOT}/scripts/petcare_backup_create.sh" | tee "${OUT}/logs/backup_create.log"

BACKUP_ZIP="${OUT}/backup.zip"
if [ ! -f "${BACKUP_ZIP}" ]; then
  # backup_create writes OUT_DIR.zip; OUT_DIR is ${OUT}/backup -> zip at ${OUT}/backup.zip
  # Enforce existence.
  echo "FATAL: expected BACKUP_ZIP not found: ${BACKUP_ZIP}" | tee -a "${OUT}/logs/error.log"
  exit 3
fi

echo ""
echo "=== STEP 2: RESTORE APPLY (CLEAN ROOT) ==="
RESTORE_ROOT="${OUT}/restore_root"
rm -rf "${RESTORE_ROOT}"
mkdir -p "${RESTORE_ROOT}"
# restore_root must be empty; use a new empty dir inside it
RESTORE_TARGET="${RESTORE_ROOT}/applied"
mkdir -p "${RESTORE_TARGET}"

export BACKUP_ZIP
export RESTORE_ROOT="${RESTORE_TARGET}"
bash "${REPO_ROOT}/scripts/petcare_restore_apply.sh" | tee "${OUT}/logs/restore_apply.log"

echo ""
echo "=== STEP 3: POST-RESTORE VALIDATION (IN-PLACE CHECKS ON REPO) ==="
# NOTE: We validate the repo itself for governance readiness. The restore is a proof artifact.
# (If you want a full "run from restored tree" later, that becomes PH-L2B.)

bash "${REPO_ROOT}/scripts/petcare_verification_index_sidecar_guard.sh" | tee "${OUT}/logs/index_sidecar_guard.log"

python3 "${REPO_ROOT}/scripts/petcare_verification_index_generate.py" --write --ts_utc "${TS_UTC}" \
  | tee "${OUT}/logs/index_generate_write.log"

bash "${REPO_ROOT}/scripts/petcare_verification_index_sidecar_write.sh" \
  | tee "${OUT}/logs/index_sidecar_write.log"

bash "${REPO_ROOT}/scripts/petcare_ci_gates.sh" | tee "${OUT}/logs/ci_gates.log"

t1="$(date +%s)"
dt="$((t1 - t0))"
echo "total_recovery_seconds=${dt}" | tee "${OUT}/logs/rto.log"

echo ""
echo "=== STEP 4: RTO ENFORCEMENT ==="
if [ "${dt}" -gt "${RTO_MAX_SECONDS}" ]; then
  echo "FAIL: RTO exceeded (dt=${dt}s > max=${RTO_MAX_SECONDS}s)" | tee -a "${OUT}/logs/rto.log"
  exit 22
fi
echo "PASS: RTO within budget (dt=${dt}s <= max=${RTO_MAX_SECONDS}s)" | tee -a "${OUT}/logs/rto.log"

echo ""
echo "=== SNAPSHOT CONTROL FILES ==="
snap=(
  "scripts/petcare_backup_create.sh"
  "scripts/petcare_restore_apply.sh"
  "scripts/petcare_ci_gates.sh"
  "scripts/petcare_ph_l2_closure_pack.sh"
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
m={
  "phase":"${PHASE}",
  "timestamp_utc":"${TS_UTC}",
  "rto_max_seconds": int("${RTO_MAX_SECONDS}"),
  "file_count":len(files),
  "files":files
}
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
