#!/usr/bin/env bash
set -euo pipefail

PACK="PETCARE-PH44B-CLOSURE"
TS_UTC="$(date -u +"%Y%m%dT%H%M%SZ")"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

OUT_ROOT="${REPO_ROOT}/evidence_output/${PACK}"
OUT="${OUT_ROOT}/${TS_UTC}"

ZIP_IN="${1:-}"
if [ -z "${ZIP_IN}" ]; then
  ZIP_IN="$(ls -1t "${REPO_ROOT}/evidence_output/PETCARE-PH43B-CLOSURE"/PETCARE-PH43B-CLOSURE_*.zip 2>/dev/null | head -1 || true)"
fi

if [ -z "${ZIP_IN}" ] || [ ! -f "${ZIP_IN}" ]; then
  echo "ERROR: input zip missing. Provide arg1 or ensure a PH43-B zip exists."
  exit 2
fi

echo "=============================================="
echo "PetCare PH44-B CLOSURE PACK"
echo "pack=${PACK}"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "zip_in=${ZIP_IN}"
echo "=============================================="

echo "=== PRECHECK: CLEAN TREE REQUIRED ==="
if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: repo is dirty"
  git status -sb
  exit 3
fi

mkdir -p "${OUT}/input" "${OUT}/verify" "${OUT}/EVIDENCE" "${OUT}/snapshots"
mkdir -p "${OUT}/EVIDENCE/verify_results"

echo "=== COPY INPUT ZIP (+ optional sidecar) ==="
cp -p "${ZIP_IN}" "${OUT}/input/INPUT.zip"
if [ -f "${ZIP_IN}.sha256" ]; then
  cp -p "${ZIP_IN}.sha256" "${OUT}/input/INPUT.zip.sha256"
fi

echo "=== RUN GENERIC VERIFIER ==="
bash "${REPO_ROOT}/scripts/petcare_verify_closure_zip.sh" "${OUT}/input/INPUT.zip" "${OUT}/verify"

echo "=== STABILIZE VERIFIER OUTPUTS (PH44B-OWNED PATHS) ==="
if [ -f "${OUT}/verify/results/VERIFY_RESULT.json" ]; then
  cp -p "${OUT}/verify/results/VERIFY_RESULT.json" "${OUT}/EVIDENCE/verify_results/VERIFY_RESULT.json"
else
  echo "ERROR: missing verifier result: ${OUT}/verify/results/VERIFY_RESULT.json"
  exit 4
fi

if [ -f "${OUT}/verify/results/VERIFY_REPORT.md" ]; then
  cp -p "${OUT}/verify/results/VERIFY_REPORT.md" "${OUT}/EVIDENCE/verify_results/VERIFY_REPORT.md"
else
  echo "ERROR: missing verifier report: ${OUT}/verify/results/VERIFY_REPORT.md"
  exit 5
fi

echo "=== WRITE EVIDENCE REPORT ==="
cat > "${OUT}/EVIDENCE/PH44B_VERIFY_CLOSURE_ZIP_REPORT.md" <<EOM
# PH44-B — Generic Closure ZIP Verification Report

ts_utc: ${TS_UTC}  
repo_root: ${REPO_ROOT}  
git_head: $(git rev-parse HEAD)  
git_describe: $(git describe --tags --dirty --always)  

input_zip (provided): ${ZIP_IN}  
input_zip (copied): ${OUT}/input/INPUT.zip  

Verifier outputs (verifier-native paths):
- verify/results/VERIFY_RESULT.json
- verify/results/VERIFY_REPORT.md

Verifier outputs (PH44B-owned stable paths):
- EVIDENCE/verify_results/VERIFY_RESULT.json
- EVIDENCE/verify_results/VERIFY_REPORT.md
EOM

echo "=== PACK MANIFEST (PH44-B) ==="
INPUT_SHA="$(shasum -a 256 "${ZIP_IN}" | awk '{print $1}')"
cat > "${OUT}/MANIFEST.json" <<EOM
{
  "pack": "${PACK}",
  "ts_utc": "${TS_UTC}",
  "repo_root": "${REPO_ROOT}",
  "git_head": "$(git rev-parse HEAD)",
  "git_describe": "$(git describe --tags --dirty --always)",
  "input_zip": {
    "path_provided": "${ZIP_IN}",
    "sha256": "${INPUT_SHA}"
  },
  "files": {
    "input_zip_copy": "input/INPUT.zip",
    "verifier_result": "EVIDENCE/verify_results/VERIFY_RESULT.json",
    "verifier_report": "EVIDENCE/verify_results/VERIFY_REPORT.md",
    "evidence_report": "EVIDENCE/PH44B_VERIFY_CLOSURE_ZIP_REPORT.md"
  }
}
EOM

echo "=== SNAPSHOT REPO SCRIPTS ==="
for f in \
  "scripts/petcare_verify_closure_zip.sh" \
  "scripts/petcare_ph44b_closure_pack.sh"
do
  if [ -f "${REPO_ROOT}/${f}" ]; then
    mkdir -p "${OUT}/snapshots/$(dirname "${f}")"
    cp -p "${REPO_ROOT}/${f}" "${OUT}/snapshots/${f}"
  fi
done

echo "=== SHA256 LIST (DETERMINISTIC; NO SELF-REFERENCE) ==="
TMP_SHA="${OUT}/.closure_sha256.tmp"
rm -f "${TMP_SHA}"
find "${OUT}" -type f \
  ! -name "closure_sha256.txt" \
  ! -name ".closure_sha256.tmp" \
  -print0 \
| LC_ALL=C sort -z \
| xargs -0 shasum -a 256 \
> "${TMP_SHA}"
mv -f "${TMP_SHA}" "${OUT}/closure_sha256.txt"

echo "=== ZIP ==="
mkdir -p "${OUT_ROOT}"
cd "${OUT_ROOT}" || exit 1
BASE="$(basename "${OUT}")"
ZIP="${PACK}_${BASE}.zip"
rm -f "${ZIP}" "${ZIP}.sha256"
zip -r "${ZIP}" "${BASE}" >/dev/null
shasum -a 256 "${ZIP}" > "${ZIP}.sha256"

echo "PASS ${PACK}"
echo "out=${OUT}"
echo "zip=${OUT_ROOT}/${ZIP}"
echo "zip_sha256=${OUT_ROOT}/${ZIP}.sha256"
