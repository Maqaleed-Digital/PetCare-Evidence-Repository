#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

PY_BIN="python3"
if [ -x ".venv/bin/python" ]; then
  PY_BIN=".venv/bin/python"
fi

BASELINE_DIR="ops/ci_baselines"
POLICY_BASELINE="${BASELINE_DIR}/policy_digest.sha256"
REGISTRY_BASELINE="${BASELINE_DIR}/registry_digest.sha256"

POLICY_CANDIDATES=(
  "ops/policy_digest.json"
  "ops/policy_digest.txt"
  "ops/policy_digest.md"
  "ops/policy_digest.yaml"
  "ops/policy_digest.yml"
  "ops/policy_digest.sha256"
  "EVIDENCE/policy_digest.json"
  "EVIDENCE/policy_digest.txt"
)

REGISTRY_CANDIDATES=(
  "ops/gate_registry.json"
  "ops/gate_registry.csv"
  "ops/gate_registry.txt"
  "ops/registry_digest.json"
  "ops/registry_digest.txt"
  "EVIDENCE/gate_registry.json"
  "EVIDENCE/gate_registry.csv"
)

pick_first_existing() {
  local arr_name="$1"
  local -n arr="$arr_name"
  local f
  for f in "${arr[@]}"; do
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

echo "=== SEED BASELINES (DETERMINISTIC) ==="
echo "repo_root=${REPO_ROOT}"
echo "python_bin=${PY_BIN}"

policy_artifact=""
if ! policy_artifact="$(pick_first_existing POLICY_CANDIDATES)"; then
  echo "POLICY_ARTIFACT_MISSING"
  printf "%s\n" "${POLICY_CANDIDATES[@]}"
  exit 4
fi

registry_artifact=""
if ! registry_artifact="$(pick_first_existing REGISTRY_CANDIDATES)"; then
  echo "REGISTRY_ARTIFACT_MISSING"
  printf "%s\n" "${REGISTRY_CANDIDATES[@]}"
  exit 4
fi

policy_sha="$(canonical_sha256 "${policy_artifact}")"
registry_sha="$(canonical_sha256 "${registry_artifact}")"

echo "${policy_sha}" > "${POLICY_BASELINE}"
echo "${registry_sha}" > "${REGISTRY_BASELINE}"

echo "SEEDED policy baseline: ${POLICY_BASELINE}"
echo "  artifact=${policy_artifact}"
echo "  sha256=${policy_sha}"

echo "SEEDED registry baseline: ${REGISTRY_BASELINE}"
echo "  artifact=${registry_artifact}"
echo "  sha256=${registry_sha}"

echo "=== BASELINE DIR LIST ==="
ls -la "${BASELINE_DIR}" | sed -n '1,200p'
