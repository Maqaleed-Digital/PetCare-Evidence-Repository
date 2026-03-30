#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIR="${REPO}/evidence_output"

MAX_MB="${MAX_MB:-4096}"

echo "=== EVIDENCE SIZE GUARD ==="
echo "repo=${REPO}"
echo "dir=${DIR}"
echo "max_mb=${MAX_MB}"

if [ ! -d "${DIR}" ]; then
  echo "EVIDENCE_DIR_MISSING=PASS (no evidence_output yet)"
  exit 0
fi

# macOS: du -sk = KiB
kb="$(du -sk "${DIR}" | awk '{print $1}')"
if [ -z "${kb}" ]; then
  echo "FAIL: could not compute du size"
  exit 20
fi

mb="$(( (kb + 1023) / 1024 ))"

echo "evidence_kb=${kb}"
echo "evidence_mb=${mb}"

if [ "${mb}" -gt "${MAX_MB}" ]; then
  echo "FAIL: evidence_output too large (mb=${mb} > max_mb=${MAX_MB})"
  echo "HINT: run scripts/petcare_evidence_prune.sh --apply --keep 5"
  exit 21
fi

echo "RESULT=PASS"
exit 0
