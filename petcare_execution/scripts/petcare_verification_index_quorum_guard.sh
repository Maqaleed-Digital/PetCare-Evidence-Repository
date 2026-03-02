#!/usr/bin/env bash
set -euo pipefail

# PH64 guard: enforce real index meets quorum (rc must be 0).
# No-guessing: requires exact path FND/VERIFICATION_INDEX.json.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INDEX="${REPO_ROOT}/FND/VERIFICATION_INDEX.json"
VERIFIER="${REPO_ROOT}/scripts/petcare_verification_index_verify.py"

if [ ! -f "${INDEX}" ]; then
  echo "FATAL: missing index: ${INDEX}"
  exit 3
fi
if [ ! -f "${VERIFIER}" ]; then
  echo "FATAL: missing verifier: ${VERIFIER}"
  exit 3
fi

echo "=== PH64 INDEX QUORUM GUARD ==="
echo "index=${INDEX}"

set +e
python3 "${VERIFIER}" --index "${INDEX}"
rc=$?
set -e

echo "verifier_rc=${rc}"

if [ "${rc}" -ne 0 ]; then
  echo "FAIL: real verification index does not satisfy quorum/integrity (expected rc=0)."
  exit 64
fi

echo "OK: real verification index satisfies quorum/integrity"
