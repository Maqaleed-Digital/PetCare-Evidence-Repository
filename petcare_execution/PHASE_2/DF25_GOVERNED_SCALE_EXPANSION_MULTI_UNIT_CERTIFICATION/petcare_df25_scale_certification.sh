#!/usr/bin/env bash
set -euo pipefail

FAIL=0

if [ -z "${UNIT_DEFINED:-}" ]; then
  echo "FAIL: UNIT_DEFINED missing"
  FAIL=1
fi

if [ -z "${CERTIFICATION_APPROVED:-}" ]; then
  echo "FAIL: CERTIFICATION_APPROVED missing"
  FAIL=1
fi

if [ "$FAIL" -eq 1 ]; then
  echo "DF25 SCALE_BLOCKED"
  exit 1
fi

echo "DF25 GOVERNED_SCALE_ACTIVE"
