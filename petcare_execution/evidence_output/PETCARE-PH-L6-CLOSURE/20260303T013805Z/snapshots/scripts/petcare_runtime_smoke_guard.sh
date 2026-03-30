#!/usr/bin/env bash
set -euo pipefail

need=(
  "docs/RUNTIME_HEALTH_CONTRACT.md"
  "scripts/petcare_health_server.py"
  "scripts/petcare_runtime_smoke.sh"
)

missing=0
for f in "${need[@]}"; do
  if [ ! -f "${f}" ]; then
    echo "MISSING_REQUIRED_FILE=${f}"
    missing=1
  fi
done

if [ "${missing}" -ne 0 ]; then
  echo "FATAL: PH-L6 surface missing"
  exit 66
fi

echo "OK PH-L6 surface guard PASS"
