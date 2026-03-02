#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INDEX="${REPO_ROOT}/FND/VERIFICATION_INDEX.json"
SIDECAR="${REPO_ROOT}/FND/VERIFICATION_INDEX.sha256"

if [ ! -f "${INDEX}" ]; then
  echo "FATAL: missing index: ${INDEX}"
  exit 3
fi

sha="$(shasum -a 256 "${INDEX}" | awk '{print $1}')"
tmp="$(mktemp)"
printf "%s  %s\n" "${sha}" "VERIFICATION_INDEX.json" > "${tmp}"
mv -f "${tmp}" "${SIDECAR}"

echo "OK wrote sidecar: ${SIDECAR}"
echo "index_sha256=${sha}"
