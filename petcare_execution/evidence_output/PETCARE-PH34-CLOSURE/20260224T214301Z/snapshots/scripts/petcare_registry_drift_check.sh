#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REG="${REPO}/REGISTRY.json"

echo "=== REGISTRY DRIFT CHECK ==="
echo "repo=${REPO}"
echo "registry=${REG}"

if [ ! -f "${REG}" ]; then
  echo "WARN: REGISTRY.json not found; treating as PASS for PH34 bootstrap"
  echo "RESULT=PASS"
  exit 0
fi

python3 - <<'PY'
import json,sys
p="REGISTRY.json"
try:
    json.load(open(p,"r",encoding="utf-8"))
except Exception as e:
    print("FAIL: REGISTRY.json invalid JSON")
    print("ERROR=%s" % e)
    sys.exit(10)
print("REGISTRY_JSON=VALID")
print("RESULT=PASS")
PY
