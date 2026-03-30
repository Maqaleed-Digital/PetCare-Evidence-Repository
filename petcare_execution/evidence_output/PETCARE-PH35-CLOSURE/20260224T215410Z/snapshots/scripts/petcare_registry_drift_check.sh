#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REG="${REPO}/REGISTRY.json"
PIN="${REPO}/REGISTRY.sha256"

echo "=== REGISTRY DRIFT CHECK ==="
echo "repo=${REPO}"
echo "registry=${REG}"
echo "pin=${PIN}"

if [ ! -f "${REG}" ]; then
  echo "FAIL: REGISTRY.json missing"
  exit 20
fi

if [ ! -f "${PIN}" ]; then
  echo "FAIL: REGISTRY.sha256 missing"
  exit 21
fi

if [ ! -s "${REG}" ]; then
  echo "FAIL: REGISTRY.json empty"
  exit 22
fi

python3 - <<'PY'
import json,sys
try:
    json.load(open("REGISTRY.json","r",encoding="utf-8"))
except Exception as e:
    print("FAIL: REGISTRY.json invalid JSON")
    print("ERROR=%s" % e)
    sys.exit(30)
print("REGISTRY_JSON=VALID")
PY

want="$(cat "${PIN}" | tr -d '[:space:]')"
if [ -z "${want}" ]; then
  echo "FAIL: REGISTRY.sha256 empty"
  exit 23
fi

have="$(shasum -a 256 "${REG}" | awk '{print $1}')"

echo "REGISTRY_SHA_HAVE=${have}"
echo "REGISTRY_SHA_WANT=${want}"

if [ "${have}" != "${want}" ]; then
  echo "FAIL: registry drift detected (REGISTRY.json != REGISTRY.sha256)"
  exit 24
fi

echo "RESULT=PASS"
exit 0
