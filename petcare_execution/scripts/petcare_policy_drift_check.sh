#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POLICY="${REPO}/POLICY.md"
PIN="${REPO}/POLICY.sha256"

echo "=== POLICY DRIFT CHECK ==="
echo "repo=${REPO}"
echo "policy=${POLICY}"
echo "pin=${PIN}"

if [ ! -f "${POLICY}" ]; then
  echo "FAIL: POLICY.md missing"
  exit 10
fi

if [ ! -f "${PIN}" ]; then
  echo "FAIL: POLICY.sha256 missing"
  exit 11
fi

want="$(cat "${PIN}" | tr -d '[:space:]')"
if [ -z "${want}" ]; then
  echo "FAIL: POLICY.sha256 empty"
  exit 12
fi

have="$(shasum -a 256 "${POLICY}" | awk '{print $1}')"

echo "POLICY_SHA_HAVE=${have}"
echo "POLICY_SHA_WANT=${want}"

if [ "${have}" != "${want}" ]; then
  echo "FAIL: policy drift detected (POLICY.md != POLICY.sha256)"
  exit 13
fi

echo "RESULT=PASS"
exit 0
