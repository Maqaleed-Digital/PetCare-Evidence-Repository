#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

PY_BIN="python3"
if [ -x ".venv/bin/python" ]; then
  PY_BIN=".venv/bin/python"
fi

BASELINE_DIR="ops/ci_baselines"
BASELINE_FILE="${BASELINE_DIR}/registry_digest.sha256"

CANDIDATES=(
  "ops/gate_registry.json"
  "ops/gate_registry.csv"
  "ops/gate_registry.txt"
  "ops/registry_digest.json"
  "ops/registry_digest.txt"
  "EVIDENCE/gate_registry.json"
  "EVIDENCE/gate_registry.csv"
)

pick_artifact() {
  local f
  for f in "${CANDIDATES[@]}"; do
    if [ -f "${f}" ]; then
      echo "${f}"
      return 0
    fi
  done
  return 1
}

canonical_sha256() {
  local f="$1"
  case "${f}" in
    *.json)
      "${PY_BIN}" - <<PY
import json, sys, hashlib
p=sys.argv[1]
obj=json.load(open(p,"r",encoding="utf-8"))
data=json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode("utf-8")
print(hashlib.sha256(data).hexdigest())
PY "${f}"
      ;;
    *)
      shasum -a 256 "${f}" | awk '{print $1}'
      ;;
  esac
}

mkdir -p "${BASELINE_DIR}"

artifact=""
if ! artifact="$(pick_artifact)"; then
  echo "REGISTRY_ARTIFACT_MISSING"
  printf "%s\n" "${CANDIDATES[@]}"
  exit 4
fi

cur="$(canonical_sha256 "${artifact}")"

if [ ! -f "${BASELINE_FILE}" ]; then
  echo "REGISTRY_BASELINE_MISSING ${BASELINE_FILE}"
  echo "artifact=${artifact}"
  echo "current_sha256=${cur}"
  exit 4
fi

want="$(tr -d ' \n\r\t' < "${BASELINE_FILE}")"

if [ "${cur}" != "${want}" ]; then
  echo "REGISTRY_DRIFT_DETECTED"
  echo "artifact=${artifact}"
  echo "baseline_sha256=${want}"
  echo "current_sha256=${cur}"
  exit 2
fi

echo "REGISTRY_DRIFT_OK"
echo "artifact=${artifact}"
echo "sha256=${cur}"
