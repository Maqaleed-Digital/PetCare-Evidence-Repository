#!/usr/bin/env bash
set -euo pipefail

need=(
  "scripts/petcare_remote_smoke.sh"
)

missing=0
for f in "${need[@]}"; do
  if [ ! -f "${f}" ]; then
    echo "MISSING_REQUIRED_FILE=${f}"
    missing=1
  fi
done

if [ "${missing}" -ne 0 ]; then
  echo "FATAL: PH-L7 deployment proof surface missing"
  exit 75
fi

echo "OK PH-L7 deployment proof guard PASS"
