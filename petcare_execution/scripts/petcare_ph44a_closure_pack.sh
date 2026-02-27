#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

PACK="PETCARE-PH44A-CLOSURE"
TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PACK}"
OUT="${OUT_ROOT}/${TS_UTC}"

PH43B_ZIP="${PH43B_ZIP:-${1:-}}"
if [ -z "${PH43B_ZIP}" ]; then echo "ERROR: PH43B_ZIP required"; exit 2; fi
if [ ! -f "${PH43B_ZIP}" ]; then echo "ERROR: PH43B_ZIP not found: ${PH43B_ZIP}"; exit 3; fi

echo "=============================================="
echo "PetCare PH44-A CLOSURE PACK"
echo "pack=${PACK}"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "ph43b_zip=${PH43B_ZIP}"
echo "=============================================="

if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: repo is dirty"; git status -sb; exit 4
fi

mkdir -p "${OUT}/input" "${OUT}/EVIDENCE" "${OUT}/snapshots" "${OUT}/verify"
cp -p "${PH43B_ZIP}" "${OUT}/input/PH43B_INPUT.zip"
shasum -a 256 "${OUT}/input/PH43B_INPUT.zip" > "${OUT}/input/PH43B_INPUT.zip.sha256"

bash "scripts/petcare_ph44_verify_ph43b_zip.sh" "${OUT}/input/PH43B_INPUT.zip" "${OUT}/verify"

cp -p "${OUT}/verify/results/PH44_VERIFY_REPORT.md" "${OUT}/EVIDENCE/PH44A_VERIFICATION_REPORT.md"
cp -p "${OUT}/verify/results/PH44_VERIFY_RESULT.json" "${OUT}/EVIDENCE/PH44A_VERIFICATION_RESULT.json"
cp -p "${OUT}/verify/logs/ph44_verify_log.txt" "${OUT}/EVIDENCE/PH44A_VERIFICATION_LOG.txt"

cat > "${OUT}/MANIFEST.json" <<EOF
{"pack":"${PACK}","ts_utc":"${TS_UTC}","git_head":"$(git rev-parse HEAD)","git_describe":"$(git describe --tags --dirty --always)"}
EOF

find "${OUT}" -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 > "${OUT}/closure_sha256.txt"

cd "${OUT_ROOT}" || exit 1
BASE="$(basename "${OUT}")"
ZIP="${PACK}_${BASE}.zip"
rm -f "${ZIP}" "${ZIP}.sha256"
zip -r "${ZIP}" "${BASE}" >/dev/null
shasum -a 256 "${ZIP}" > "${ZIP}.sha256"

echo "PASS ${PACK}"
echo "zip=${OUT_ROOT}/${ZIP}"
