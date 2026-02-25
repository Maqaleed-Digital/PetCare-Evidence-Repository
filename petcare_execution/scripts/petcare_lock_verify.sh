#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${REPO}/.venv/bin/python"
LOCK="${REPO}/requirements.lock"

echo "=== LOCK VERIFY ==="
echo "repo=${REPO}"
echo "python=${PY}"
echo "lock=${LOCK}"

if [ ! -x "${PY}" ]; then
  echo "FAIL: venv python missing at ${PY}"
  exit 20
fi

if [ ! -f "${LOCK}" ]; then
  echo "FAIL: lockfile missing: requirements.lock"
  exit 21
fi

if [ ! -s "${LOCK}" ]; then
  echo "FAIL: lockfile empty: requirements.lock"
  exit 22
fi

TMP_DIR="${REPO}/.tmp_lock_verify"
mkdir -p "${TMP_DIR}"
GEN="${TMP_DIR}/generated.freeze.sorted.txt"
LOCK_NORM="${TMP_DIR}/lock.sorted.txt"

# Normalize lock: remove blank lines, sort stable
LC_ALL=C sed '/^[[:space:]]*$/d' "${LOCK}" | LC_ALL=C sort > "${LOCK_NORM}"

# Generate current environment freeze (normalized, sorted)
"${PY}" -m pip freeze | LC_ALL=C sort > "${GEN}"

# Compare
if ! diff -u "${LOCK_NORM}" "${GEN}" >/dev/null; then
  echo "FAIL: requirements.lock does not match current environment (pip freeze)."
  echo "HINT: regenerate requirements.lock from the intended environment."
  echo ""
  echo "=== DIFF (first 200 lines) ==="
  diff -u "${LOCK_NORM}" "${GEN}" | sed -n '1,200p' || true
  exit 23
fi

echo "LOCK_VERIFY=PASS"
exit 0
