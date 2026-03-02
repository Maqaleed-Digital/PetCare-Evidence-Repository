#!/usr/bin/env bash
set -euo pipefail

PHASE="PETCARE-PH59-CLOSURE"
TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PHASE}"
OUT="${OUT_ROOT}/${TS_UTC}"

# Recommended defaults: cap=3 (matches current), quorum=1 (non-breaking)
CAP="${CAP:-3}"
QUORUM="${QUORUM:-1}"

mkdir -p "${OUT}/logs" "${OUT}/snapshots"

echo "=============================================="
echo "PetCare PH59 CLOSURE PACK"
echo "timestamp_utc=${TS_UTC}"
echo "cap=${CAP}"
echo "quorum=${QUORUM}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "=============================================="

need=(
  "FND/VERIFICATION_POLICY.json"
  "FND/VERIFICATION_POLICY.sha256"
  "FND/VERIFICATION_POLICY_CHANGELOG.md"
  "scripts/petcare_verification_policy_verify.py"
  "scripts/petcare_verification_policy_changelog_add.py"
  "scripts/petcare_verification_policy_controls_set.py"
  "scripts/petcare_meta_verifier_governance_guard.py"
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
echo "=== STEP 1: SET CAP/QUORUM VIA TOOL (NO MANUAL EDITS) ==="
python3 "${REPO_ROOT}/scripts/petcare_verification_policy_controls_set.py" \
  --cap "${CAP}" \
  --quorum "${QUORUM}" \
  | tee "${OUT}/logs/policy_controls_set.log"

echo ""
echo "=== STEP 2: POLICY VERIFY (EXISTING TOOL) ==="
python3 "${REPO_ROOT}/scripts/petcare_verification_policy_verify.py" \
  | tee "${OUT}/logs/policy_verify.log"

echo ""
echo "=== STEP 3: PH59 GOVERNANCE GUARD (CAP/QUORUM CONSISTENCY) ==="
python3 "${REPO_ROOT}/scripts/petcare_meta_verifier_governance_guard.py" \
  | tee "${OUT}/logs/meta_verifier_governance_guard.log"

echo ""
echo "=== STEP 4: CHANGELOG APPEND (RECORD POLICY SHA) ==="
python3 "${REPO_ROOT}/scripts/petcare_verification_policy_changelog_add.py" \
  --pack "PH59-CONTROLS(cap=${CAP},quorum=${QUORUM})" \
  --ts "${TS_UTC}" \
  | tee "${OUT}/logs/changelog_add.log"

echo ""
echo "=== STEP 5 (OPTIONAL): CI GATES IF PRESENT ==="
if [ -f "${REPO_ROOT}/scripts/petcare_ci_gates.sh" ]; then
  bash "${REPO_ROOT}/scripts/petcare_ci_gates.sh" \
    | tee "${OUT}/logs/ci_gates.log"
else
  echo "SKIP: scripts/petcare_ci_gates.sh not found."
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
import json
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
  "cap": int("${CAP}"),
  "quorum": int("${QUORUM}"),
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
