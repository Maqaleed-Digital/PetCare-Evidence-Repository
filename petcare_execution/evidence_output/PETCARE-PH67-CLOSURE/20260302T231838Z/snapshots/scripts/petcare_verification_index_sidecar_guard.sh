#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INDEX="${REPO_ROOT}/FND/VERIFICATION_INDEX.json"
SIDECAR="${REPO_ROOT}/FND/VERIFICATION_INDEX.sha256"

if [ ! -f "${INDEX}" ]; then
  echo "FATAL: missing index: ${INDEX}"
  exit 3
fi
if [ ! -f "${SIDECAR}" ]; then
  echo "FATAL: missing index sidecar: ${SIDECAR}"
  exit 67
fi

actual="$(shasum -a 256 "${INDEX}" | awk '{print $1}')"
sidecar="$(awk '{print $1}' "${SIDECAR}")"

echo "index_sha256_actual=${actual}"
echo "index_sha256_sidecar=${sidecar}"

if [ "${actual}" != "${sidecar}" ]; then
  echo "FAIL: VERIFICATION_INDEX.sha256 does not match VERIFICATION_INDEX.json"
  exit 67
fi

echo "OK: index sidecar matches"
