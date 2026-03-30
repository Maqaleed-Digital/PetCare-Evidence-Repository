#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REG="${ROOT}/REGISTRY.json"
PIN="${ROOT}/REGISTRY.sha256"

echo "=== REGISTRY DRIFT CHECK ==="
echo "repo=${ROOT}"
echo "registry=${REG}"
echo "pin=${PIN}"

if [ ! -f "${REG}" ]; then
  echo "FAIL: missing REGISTRY.json"
  exit 1
fi

if [ ! -f "${PIN}" ]; then
  echo "FAIL: missing REGISTRY.sha256"
  exit 1
fi

python3 -m json.tool "${REG}" >/dev/null
echo "REGISTRY_JSON=VALID"

HAVE="$(shasum -a 256 "${REG}" | awk '{print $1}')"
WANT="$(awk '{print $1}' "${PIN}")"

echo "REGISTRY_SHA_HAVE=${HAVE}"
echo "REGISTRY_SHA_WANT=${WANT}"

if [ "${HAVE}" != "${WANT}" ]; then
  echo "FAIL: registry drift detected (REGISTRY.json != REGISTRY.sha256)"
  exit 1
fi

echo "RESULT=PASS"
