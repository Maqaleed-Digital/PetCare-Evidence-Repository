set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}" || exit 1

if [ ! -x ".venv/bin/python" ]; then
  echo "MISSING: ${ROOT}/.venv (run Phase-3 venv setup first)"
  exit 1
fi

cmd="${1:-serve}"

if [ "${cmd}" = "serve" ]; then
  exec ".venv/bin/python" -m uvicorn "FND.CODE_SCAFFOLD.app:app" --host "127.0.0.1" --port "8000"
fi

if [ "${cmd}" = "smoke" ]; then
  API="${API:-http://127.0.0.1:8000}"
  TENANT="${TENANT:-11111111-1111-1111-1111-111111111111}"

  echo "=== HEALTH ==="
  h="$(curl -sS "${API}/health" || true)"
  echo "${h}"
  echo "${h}" | grep -q '"ok":true' || { echo "FAIL: health"; exit 2; }

  echo "=== PUT missing tenant (expect error) ==="
  r1="$(curl -sS -X POST "${API}/api/platform-admin/storage/put" -H "Content-Type: application/json" -d '{"key":"k1","value":"v1","actor_id":"a"}' || true)"
  echo "${r1}"
  echo "${r1}" | grep -q 'x-tenant-id is required' || { echo "FAIL: missing tenant not rejected"; exit 3; }

  echo "=== PUT with tenant (expect ok) ==="
  r2="$(curl -sS -X POST "${API}/api/platform-admin/storage/put" -H "Content-Type: application/json" -H "x-tenant-id: ${TENANT}" -d '{"key":"k1","value":"v1","actor_id":"a"}' || true)"
  echo "${r2}"
  echo "${r2}" | grep -q '"ok":true' || { echo "FAIL: put with tenant"; exit 4; }

  echo "=== GET with tenant (expect value v1) ==="
  r3="$(curl -sS -X POST "${API}/api/platform-admin/storage/get" -H "Content-Type: application/json" -H "x-tenant-id: ${TENANT}" -d '{"key":"k1"}' || true)"
  echo "${r3}"
  echo "${r3}" | grep -q '"value":"v1"' || { echo "FAIL: get value"; exit 5; }

  echo "PASS smoke"
  exit 0
fi

echo "USAGE:"
echo "  bash scripts/run_api.sh serve"
echo "  bash scripts/run_api.sh smoke"
exit 1
