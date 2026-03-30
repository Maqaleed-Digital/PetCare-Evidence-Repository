set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}" || exit 1

if [ ! -x ".venv/bin/python" ]; then
  echo "MISSING: ${ROOT}/.venv (run Phase-3 venv setup first)"
  exit 1
fi

exec ".venv/bin/python" -m uvicorn "FND.CODE_SCAFFOLD.app:app" --host "127.0.0.1" --port "8000"
