#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}" || exit 1

ARTIFACT_PATH="${1:-}"

echo "=== PROD DEPLOY ARTIFACT CONTRACT ==="
echo "repo=${ROOT}"

if [ -z "${ARTIFACT_PATH}" ]; then
  echo "NOTE=No artifact provided; contract is SKIP (PASS-by-absence)"
  echo "RESULT=PASS"
  exit 0
fi

if [ ! -f "${ARTIFACT_PATH}" ]; then
  echo "RESULT=FAIL"
  echo "MISSING_ARTIFACT=${ARTIFACT_PATH}"
  exit 1
fi

SHA="$(shasum -a 256 "${ARTIFACT_PATH}" | awk '{print $1}')"
SIZE_BYTES="$(wc -c < "${ARTIFACT_PATH}" | tr -d ' ')"

echo "ARTIFACT_PATH=${ARTIFACT_PATH}"
echo "ARTIFACT_SHA256=${SHA}"
echo "ARTIFACT_SIZE_BYTES=${SIZE_BYTES}"
echo "RESULT=PASS"
