#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

BASELINE_DIR="ops/ci_baselines"
mkdir -p "${BASELINE_DIR}"

seed_one() {
  local kind="$1"
  local probe_script="$2"
  local baseline_file="$3"

  set +e
  bash "${probe_script}" > "${BASELINE_DIR}/_${kind}_probe.txt" 2>&1
  rc=$?
  set -e

  if grep -q "^artifact=" "${BASELINE_DIR}/_${kind}_probe.txt"; then
    artifact="$(grep "^artifact=" "${BASELINE_DIR}/_${kind}_probe.txt" | head -1 | cut -d'=' -f2-)"
  else
    artifact="$(grep -E "artifact=" "${BASELINE_DIR}/_${kind}_probe.txt" | head -1 | cut -d'=' -f2-)"
  fi

  if [ -n "${artifact}" ] && [ -f "${artifact}" ]; then
    if [[ "${artifact}" == *.json ]]; then
      sha="$(.venv/bin/python - <<PY
import json, hashlib
p="${artifact}"
obj=json.load(open(p,"r",encoding="utf-8"))
data=json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode("utf-8")
print(hashlib.sha256(data).hexdigest())
PY
)"
    else
      sha="$(shasum -a 256 "${artifact}" | awk '{print $1}')"
    fi
    echo "${sha}" > "${baseline_file}"
    echo "SEEDED ${baseline_file} artifact=${artifact} sha256=${sha}"
    return 0
  fi

  echo "FAILED_SEED kind=${kind}"
  cat "${BASELINE_DIR}/_${kind}_probe.txt"
  return 1
}

seed_one "policy" "scripts/petcare_policy_drift_check.sh" "${BASELINE_DIR}/policy_digest.sha256"
seed_one "registry" "scripts/petcare_registry_drift_check.sh" "${BASELINE_DIR}/registry_digest.sha256"

echo "=== BASELINES ==="
ls -la "${BASELINE_DIR}" | sed -n '1,200p'
