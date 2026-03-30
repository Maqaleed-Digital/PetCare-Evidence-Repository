#!/usr/bin/env bash
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)" || exit 1

PY_BIN="python3"
if [ -x ".venv/bin/python" ]; then PY_BIN=".venv/bin/python"; fi

BASELINE_DIR="ops/ci_baselines"
BASELINE_FILE="${BASELINE_DIR}/policy_digest.sha256"
ARTIFACT="ops/ph12_policy_digest.json"

mkdir -p "${BASELINE_DIR}"

if [ ! -f "${ARTIFACT}" ]; then
  echo "POLICY_ARTIFACT_MISSING ${ARTIFACT}"
  exit 4
fi

cur="$("${PY_BIN}" -c 'import json,hashlib; import sys; p=sys.argv[1]; obj=json.load(open(p,"r",encoding="utf-8")); data=json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8"); print(hashlib.sha256(data).hexdigest())' "${ARTIFACT}")"

if [ ! -f "${BASELINE_FILE}" ]; then
  echo "POLICY_BASELINE_MISSING ${BASELINE_FILE}"
  echo "artifact=${ARTIFACT}"
  echo "current_sha256=${cur}"
  exit 4
fi

want="$(tr -d " 
	" < "${BASELINE_FILE}")"

if [ "${cur}" != "${want}" ]; then
  echo "POLICY_DRIFT_DETECTED"
  echo "artifact=${ARTIFACT}"
  echo "baseline_sha256=${want}"
  echo "current_sha256=${cur}"
  exit 2
fi

echo "POLICY_DRIFT_OK"
echo "artifact=${ARTIFACT}"
echo "sha256=${cur}"
