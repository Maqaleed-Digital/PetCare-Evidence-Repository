#!/usr/bin/env bash
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)" || exit 1

PY_BIN="python3"
if [ -x ".venv/bin/python" ]; then PY_BIN=".venv/bin/python"; fi

BASELINE_DIR="ops/ci_baselines"
mkdir -p "${BASELINE_DIR}"

POLICY_ARTIFACT="ops/ph12_policy_digest.json"
REGISTRY_ARTIFACT="ops/ph12_gate_registry.json"

test -f "${POLICY_ARTIFACT}" || { echo "POLICY_ARTIFACT_MISSING ${POLICY_ARTIFACT}"; exit 4; }
test -f "${REGISTRY_ARTIFACT}" || { echo "REGISTRY_ARTIFACT_MISSING ${REGISTRY_ARTIFACT}"; exit 4; }

policy_sha="$("${PY_BIN}" -c 'import json,hashlib; import sys; p=sys.argv[1]; obj=json.load(open(p,"r",encoding="utf-8")); data=json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8"); print(hashlib.sha256(data).hexdigest())' "${POLICY_ARTIFACT}")"
registry_sha="$("${PY_BIN}" -c 'import json,hashlib; import sys; p=sys.argv[1]; obj=json.load(open(p,"r",encoding="utf-8")); data=json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8"); print(hashlib.sha256(data).hexdigest())' "${REGISTRY_ARTIFACT}")"

echo "${policy_sha}" > "${BASELINE_DIR}/policy_digest.sha256"
echo "${registry_sha}" > "${BASELINE_DIR}/registry_digest.sha256"

echo "SEEDED ${BASELINE_DIR}/policy_digest.sha256 sha256=${policy_sha}"
echo "SEEDED ${BASELINE_DIR}/registry_digest.sha256 sha256=${registry_sha}"
ls -la "${BASELINE_DIR}" | sed -n "1,200p"
