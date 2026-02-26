#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

PACK="PETCARE-PH43B-CLOSURE"
TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PACK}"
OUT="${OUT_ROOT}/${TS_UTC}"

ARTIFACT_PATH="${ARTIFACT_PATH:-}"
RELEASE_TAG="${RELEASE_TAG:-}"

if [ -z "${ARTIFACT_PATH}" ]; then
  echo "ERROR: ARTIFACT_PATH is required for PH43-B closure pack"
  exit 2
fi

mkdir -p "${OUT}"

echo "=============================================="
echo "PetCare PH43-B CLOSURE PACK"
echo "pack=${PACK}"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "artifact_path=${ARTIFACT_PATH}"
echo "release_tag=${RELEASE_TAG:-"(unset)"}"
echo "=============================================="

echo "=== PRECHECK: CLEAN TREE REQUIRED ==="
if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: repo is dirty; closure pack must run on a clean tree"
  git status -sb
  exit 3
fi

echo "=== OPTIONAL: VERIFY RELEASE TAG (IF PROVIDED) ==="
if [ -n "${RELEASE_TAG}" ]; then
  bash "scripts/petcare_release_tag_verify.sh" "${RELEASE_TAG}"
else
  echo "SKIP: RELEASE_TAG not set"
fi

echo "=== ARTIFACT-BOUND ATTESTATION (REQUIRED) ==="
export OUT_DIR="${OUT}"
export ARTIFACT_PATH="${ARTIFACT_PATH}"
export RELEASE_TAG="${RELEASE_TAG:-"(unset)"}"
bash "scripts/petcare_prod_artifact_bound_attest.sh"

REC_JSON="${OUT}/attestation/ARTIFACT_BOUND_ATTESTATION.json"
if [ ! -f "${REC_JSON}" ]; then
  echo "ERROR: missing attestation record: ${REC_JSON}"
  exit 4
fi

ARTIFACT_SHA256="$(cat "${REC_JSON}" | tr -d '
' | sed -n 's/.*"sha256":[ ]*"\([^"]*\)".*/\1/p')"
ARTIFACT_NAME="$(cat "${REC_JSON}" | tr -d '
' | sed -n 's/.*"name":[ ]*"\([^"]*\)".*/\1/p')"

if [ -z "${ARTIFACT_SHA256}" ] || [ -z "${ARTIFACT_NAME}" ]; then
  echo "ERROR: failed to extract artifact sha256/name from attestation record"
  exit 5
fi

echo "=== WRITE EVIDENCE REPORT ==="
mkdir -p "${OUT}/EVIDENCE"
REPORT="${OUT}/EVIDENCE/PH43B_ARTIFACT_BOUND_ATTESTATION_REPORT.md"

cat > "${REPORT}" <<EOF
# PH43-B — Artifact-Bound Production Attestation Report

ts_utc: ${TS_UTC}  
repo_root: ${REPO_ROOT}  
git_head: $(git rev-parse HEAD)  
git_describe: $(git describe --tags --dirty --always)  
release_tag: ${RELEASE_TAG:-"(unset)"}  

## Artifact Binding
ARTIFACT_PATH (provided): ${ARTIFACT_PATH}  
Artifact name: ${ARTIFACT_NAME}  
Artifact sha256: ${ARTIFACT_SHA256}  

## Attestation Record
- ${REC_JSON}

## Notes
- This pack enforces clean-tree attestation (fails if repo is dirty).
- Artifact is copied into the pack under: artifact/${ARTIFACT_NAME}
EOF

echo "=== PACK MANIFEST (PH43-B) ==="
MANIFEST="${OUT}/MANIFEST.json"
cat > "${MANIFEST}" <<EOF
{
  "pack": "${PACK}",
  "ts_utc": "${TS_UTC}",
  "repo_root": "${REPO_ROOT}",
  "git_head": "$(git rev-parse HEAD)",
  "git_describe": "$(git describe --tags --dirty --always)",
  "release_tag": "${RELEASE_TAG:-"(unset)"}",
  "artifact": {
    "path_provided": "${ARTIFACT_PATH}",
    "name": "${ARTIFACT_NAME}",
    "sha256": "${ARTIFACT_SHA256}"
  },
  "files": {
    "attestation_record": "attestation/ARTIFACT_BOUND_ATTESTATION.json",
    "evidence_report": "EVIDENCE/PH43B_ARTIFACT_BOUND_ATTESTATION_REPORT.md",
    "artifact_copy": "artifact/${ARTIFACT_NAME}"
  }
}
EOF

echo "=== SNAPSHOT SELECTED REPO FILES ==="
mkdir -p "${OUT}/snapshots"
cat > "${OUT}/closure_files.txt" <<EOF
scripts/petcare_release_tag_verify.sh
scripts/petcare_prod_artifact_bound_attest.sh
scripts/petcare_ph43b_closure_pack.sh
EOF

while IFS= read -r f; do
  if [ -f "${REPO_ROOT}/${f}" ]; then
    mkdir -p "${OUT}/snapshots/$(dirname "${f}")"
    cp -p "${REPO_ROOT}/${f}" "${OUT}/snapshots/${f}"
  else
    echo "MISSING_FILE=${f}" >> "${OUT}/missing_files.txt"
  fi
done < "${OUT}/closure_files.txt"

echo "=== SHA256 LIST (DETERMINISTIC) ==="
find "${OUT}" -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 > "${OUT}/closure_sha256.txt"

echo "=== ZIP ==="
mkdir -p "${OUT_ROOT}"
cd "${OUT_ROOT}" || exit 1
BASE="$(basename "${OUT}")"
ZIP="${PACK}_${BASE}.zip"
rm -f "${ZIP}" "${ZIP}.sha256"
zip -r "${ZIP}" "${BASE}" >/dev/null
shasum -a 256 "${ZIP}" > "${ZIP}.sha256"

echo "=== DONE ==="
echo "out=${OUT}"
echo "zip=${OUT_ROOT}/${ZIP}"
echo "zip_sha256=${OUT_ROOT}/${ZIP}.sha256"
echo "PASS ${PACK}"
