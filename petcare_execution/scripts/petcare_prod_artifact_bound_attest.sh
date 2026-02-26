#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

OUT_DIR="${OUT_DIR:-}"
ARTIFACT_PATH="${ARTIFACT_PATH:-}"
RELEASE_TAG="${RELEASE_TAG:-}"
ATTESTOR="${ATTESTOR:-}"

if [ -z "${OUT_DIR}" ]; then
  echo "ERROR: OUT_DIR is required"
  exit 2
fi

if [ -z "${ARTIFACT_PATH}" ]; then
  echo "ERROR: ARTIFACT_PATH is required"
  exit 3
fi

if [ ! -f "${ARTIFACT_PATH}" ]; then
  echo "ERROR: artifact not found at ARTIFACT_PATH=${ARTIFACT_PATH}"
  exit 4
fi

if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: repo is dirty; artifact-bound attestation must run on a clean tree"
  git status -sb
  exit 5
fi

mkdir -p "${OUT_DIR}/attestation" "${OUT_DIR}/artifact"

ARTIFACT_ABS="$(cd "$(dirname "${ARTIFACT_PATH}")" && pwd)/$(basename "${ARTIFACT_PATH}")"
ARTIFACT_NAME="$(basename "${ARTIFACT_ABS}")"

if command -v shasum >/dev/null 2>&1; then
  ARTIFACT_SHA256="$(shasum -a 256 "${ARTIFACT_ABS}" | awk '{print $1}')"
else
  echo "ERROR: shasum not found (required to compute sha256)"
  exit 6
fi

HEAD_SHA="$(git rev-parse HEAD)"
DESC="$(git describe --tags --dirty --always)"

if echo "${DESC}" | grep -q -- "-dirty"; then
  echo "ERROR: describe indicates dirty state (should be unreachable due to porcelain check)"
  exit 7
fi

cp -p "${ARTIFACT_ABS}" "${OUT_DIR}/artifact/${ARTIFACT_NAME}"

TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"

if [ -z "${ATTESTOR}" ]; then
  ATTESTOR="$(git config user.name || true)"
fi

if [ -z "${RELEASE_TAG}" ]; then
  RELEASE_TAG="(unset)"
fi

REC_JSON="${OUT_DIR}/attestation/ARTIFACT_BOUND_ATTESTATION.json"

cat > "${REC_JSON}" <<EOF
{
  "schema": "petcare.prod.artifact_bound_attestation.v1",
  "ts_utc": "${TS_UTC}",
  "repo_root": "${REPO_ROOT}",
  "git_head": "${HEAD_SHA}",
  "git_describe": "${DESC}",
  "release_tag": "${RELEASE_TAG}",
  "attestor": "${ATTESTOR}",
  "artifact": {
    "path_provided": "${ARTIFACT_PATH}",
    "path_resolved_abs": "${ARTIFACT_ABS}",
    "name": "${ARTIFACT_NAME}",
    "sha256": "${ARTIFACT_SHA256}"
  }
}
EOF

echo "=== ARTIFACT-BOUND ATTESTATION ==="
echo "out_dir=${OUT_DIR}"
echo "record=${REC_JSON}"
echo "artifact_name=${ARTIFACT_NAME}"
echo "artifact_sha256=${ARTIFACT_SHA256}"
echo "PASS artifact-bound attestation"
