#!/usr/bin/env bash
set -euo pipefail

HEALTH_URL="${HEALTH_URL:-}"
if [ -z "${HEALTH_URL}" ]; then
  echo "FATAL: HEALTH_URL not set"
  exit 61
fi

READY_URL="${HEALTH_URL%/health}/ready"

H="$(curl -fsS "${HEALTH_URL}")" || { echo "FATAL: health failed"; exit 62; }
R="$(curl -fsS "${READY_URL}")" || { echo "FATAL: ready failed"; exit 63; }

python3 - <<PY
import json
h=json.loads("""${H}""")
r=json.loads("""${R}""")
assert h["status"]=="ok"
assert r["status"]=="ready"
print("OK runtime smoke PASS")
PY
