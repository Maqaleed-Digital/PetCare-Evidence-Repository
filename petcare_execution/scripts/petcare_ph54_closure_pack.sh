#!/usr/bin/env bash
set -euo pipefail

PHASE="PETCARE-PH54-CLOSURE"
TS_UTC="$(date -u +"%Y%m%dT%H%M%SZ")"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PHASE}"
OUT="${OUT_ROOT}/${TS_UTC}"

PY_BIN="python3"

echo "=============================================="
echo "PetCare PH54 CLOSURE PACK"
echo "pack=${PHASE}"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "python_bin=${PY_BIN}"
echo "=============================================="

mkdir -p "${OUT}/snapshots" "${OUT}/EVIDENCE"

echo "=== COMPILE (TOOLS) ==="
${PY_BIN} -m py_compile \
  "${REPO_ROOT}/scripts/petcare_verification_policy_verify.py" \
  "${REPO_ROOT}/scripts/petcare_verification_policy_allowlist_add.py" \
  "${REPO_ROOT}/scripts/petcare_verification_index_append.py" \
  "${REPO_ROOT}/scripts/petcare_verification_index_verify.py"

echo "=== VERIFY POLICY (SHA + SCHEMA) ==="
${PY_BIN} "${REPO_ROOT}/scripts/petcare_verification_policy_verify.py" \
  --policy "${REPO_ROOT}/FND/VERIFICATION_POLICY.json" \
  --policy_sha "${REPO_ROOT}/FND/VERIFICATION_POLICY.sha256" \
  | tee "${OUT}/EVIDENCE/policy_verify_stdout.txt"

echo "=== SNAPSHOTS ==="
# Policy + sidecar
mkdir -p "${OUT}/snapshots/FND"
cp -p "${REPO_ROOT}/FND/VERIFICATION_POLICY.json" "${OUT}/snapshots/FND/VERIFICATION_POLICY.json"
cp -p "${REPO_ROOT}/FND/VERIFICATION_POLICY.sha256" "${OUT}/snapshots/FND/VERIFICATION_POLICY.sha256"

# Verification toolchain scripts (current)
mkdir -p "${OUT}/snapshots/scripts"
cp -p "${REPO_ROOT}/scripts/petcare_verification_policy_verify.py" "${OUT}/snapshots/scripts/petcare_verification_policy_verify.py"
cp -p "${REPO_ROOT}/scripts/petcare_verification_policy_allowlist_add.py" "${OUT}/snapshots/scripts/petcare_verification_policy_allowlist_add.py"
cp -p "${REPO_ROOT}/scripts/petcare_verification_index_append.py" "${OUT}/snapshots/scripts/petcare_verification_index_append.py"
cp -p "${REPO_ROOT}/scripts/petcare_verification_index_verify.py" "${OUT}/snapshots/scripts/petcare_verification_index_verify.py"

# Workflow snapshot if present (best effort)
mkdir -p "${OUT}/snapshots/.github/workflows"
if [ -f "${REPO_ROOT}/.github/workflows/verification-index-gate-final.yml" ]; then
  cp -p "${REPO_ROOT}/.github/workflows/verification-index-gate-final.yml" "${OUT}/snapshots/.github/workflows/verification-index-gate-final.yml"
else
  echo "SKIP: .github/workflows/verification-index-gate-final.yml not found" | tee "${OUT}/EVIDENCE/workflow_snapshot_skip.txt"
fi

echo "=== MANIFEST (PH54) ==="
cat > "${OUT}/MANIFEST.json" <<JSON
{
  "pack": "${PHASE}",
  "ts_utc": "${TS_UTC}",
  "repo_root": "${REPO_ROOT}",
  "artifacts": {
    "policy_json": "FND/VERIFICATION_POLICY.json",
    "policy_sha": "FND/VERIFICATION_POLICY.sha256",
    "policy_verify_log": "EVIDENCE/policy_verify_stdout.txt"
  },
  "snapshots": {
    "policy": "snapshots/FND/VERIFICATION_POLICY.json",
    "policy_sha": "snapshots/FND/VERIFICATION_POLICY.sha256",
    "tool_policy_verify": "snapshots/scripts/petcare_verification_policy_verify.py",
    "tool_policy_allowlist_add": "snapshots/scripts/petcare_verification_policy_allowlist_add.py",
    "tool_index_append": "snapshots/scripts/petcare_verification_index_append.py",
    "tool_index_verify": "snapshots/scripts/petcare_verification_index_verify.py",
    "workflow_gate": "snapshots/.github/workflows/verification-index-gate-final.yml"
  }
}
JSON

echo "=== ZIP + SHA256 ==="
ZIP="${OUT_ROOT}/${PHASE}_${TS_UTC}.zip"
rm -f "${ZIP}" "${ZIP}.sha256"
(
  cd "${OUT_ROOT}" || exit 1
  zip -r "${PHASE}_${TS_UTC}.zip" "${TS_UTC}" >/dev/null
  shasum -a 256 "${PHASE}_${TS_UTC}.zip" > "${PHASE}_${TS_UTC}.zip.sha256"
)

echo "=== SUMMARY ==="
echo "OUT=${OUT}"
echo "ZIP=${ZIP}"
echo "ZIP_SHA=${ZIP}.sha256"
echo "DONE"
