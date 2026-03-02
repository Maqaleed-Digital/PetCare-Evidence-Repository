#!/usr/bin/env bash
set -euo pipefail

PHASE="PETCARE-PH55-CLOSURE"
TS_UTC="$(date -u +"%Y%m%dT%H%M%SZ")"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PHASE}"
OUT="${OUT_ROOT}/${TS_UTC}"

echo "=============================================="
echo "PetCare PH55 CLOSURE PACK"
echo "pack=${PHASE}"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "=============================================="

mkdir -p "${OUT}/snapshots" "${OUT}/EVIDENCE"

echo "=== COMPILE (TOOLCHAIN) ==="
python3 -m py_compile "${REPO_ROOT}/scripts/petcare_verification_policy_verify.py"
python3 -m py_compile "${REPO_ROOT}/scripts/petcare_verification_policy_allowlist_add.py"
python3 -m py_compile "${REPO_ROOT}/scripts/petcare_verification_policy_change_guard.py"
python3 -m py_compile "${REPO_ROOT}/scripts/petcare_verification_index_verify.py"
python3 -m py_compile "${REPO_ROOT}/scripts/petcare_verification_index_append.py"
echo "OK compile"

echo "=== VERIFY POLICY (SHA + INVARIANTS) ==="
python3 "${REPO_ROOT}/scripts/petcare_verification_policy_verify.py" | tee "${OUT}/EVIDENCE/policy_verify_stdout.txt"

echo "=== VERIFY POLICY CHANGELOG (STRICT: LAST ENTRY MATCHES CURRENT SHA) ==="
python3 "${REPO_ROOT}/scripts/petcare_verification_policy_change_guard.py" --require_last_entry_matches \
  | tee "${OUT}/EVIDENCE/policy_changelog_guard_stdout.txt"

echo "=== SNAPSHOTS ==="
# policy artifacts
mkdir -p "${OUT}/snapshots/FND" "${OUT}/snapshots/scripts" "${OUT}/snapshots/.github/workflows"
cp -p "${REPO_ROOT}/FND/VERIFICATION_POLICY.json" "${OUT}/snapshots/FND/VERIFICATION_POLICY.json"
cp -p "${REPO_ROOT}/FND/VERIFICATION_POLICY.sha256" "${OUT}/snapshots/FND/VERIFICATION_POLICY.sha256"
cp -p "${REPO_ROOT}/FND/VERIFICATION_POLICY_CHANGELOG.md" "${OUT}/snapshots/FND/VERIFICATION_POLICY_CHANGELOG.md"

# scripts
cp -p "${REPO_ROOT}/scripts/petcare_verification_policy_verify.py" "${OUT}/snapshots/scripts/petcare_verification_policy_verify.py"
cp -p "${REPO_ROOT}/scripts/petcare_verification_policy_allowlist_add.py" "${OUT}/snapshots/scripts/petcare_verification_policy_allowlist_add.py"
cp -p "${REPO_ROOT}/scripts/petcare_verification_policy_change_guard.py" "${OUT}/snapshots/scripts/petcare_verification_policy_change_guard.py"
cp -p "${REPO_ROOT}/scripts/petcare_verification_index_verify.py" "${OUT}/snapshots/scripts/petcare_verification_index_verify.py"
cp -p "${REPO_ROOT}/scripts/petcare_verification_index_append.py" "${OUT}/snapshots/scripts/petcare_verification_index_append.py"

# workflow gate
cp -p "${REPO_ROOT}/.github/workflows/verification-index-gate-final.yml" "${OUT}/snapshots/.github/workflows/verification-index-gate-final.yml"

echo "=== MANIFEST (PH55) ==="
cat > "${OUT}/MANIFEST.json" <<JSON
{
  "pack": "${PHASE}",
  "ts_utc": "${TS_UTC}",
  "repo_root": "${REPO_ROOT}",
  "artifacts": {
    "policy_json": "FND/VERIFICATION_POLICY.json",
    "policy_sha256": "FND/VERIFICATION_POLICY.sha256",
    "policy_changelog": "FND/VERIFICATION_POLICY_CHANGELOG.md",
    "workflow_gate": ".github/workflows/verification-index-gate-final.yml",
    "tools": [
      "scripts/petcare_verification_policy_verify.py",
      "scripts/petcare_verification_policy_allowlist_add.py",
      "scripts/petcare_verification_policy_change_guard.py",
      "scripts/petcare_verification_index_append.py",
      "scripts/petcare_verification_index_verify.py"
    ]
  }
}
JSON

echo "=== ZIP + ZIP.SHA256 ==="
mkdir -p "${OUT_ROOT}"
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
