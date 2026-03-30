#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

ts="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="evidence_output/_local_debug/PH8_SCAN/${ts}"
mkdir -p "${OUT}"

echo "PH8_SCAN" > "${OUT}/title.txt"
echo "timestamp_utc=${ts}" > "${OUT}/meta.txt"
echo "repo_root=${REPO_ROOT}" >> "${OUT}/meta.txt"

{
  echo "=== PH8 SCAN REPORT ==="
  echo "timestamp_utc=${ts}"
  echo "repo_root=${REPO_ROOT}"
  echo ""
  echo "=== CANDIDATE FILES (PH8 in name/path/content) ==="
  echo ""

  echo "--- find: paths containing PH8"
  find . -type f -maxdepth 6 \
    \( -iname "*ph8*" -o -path "*PH8*" \) \
    -print | LC_ALL=C sort || true
  echo ""

  echo "--- grep: content mentions PH8"
  grep -R --line-number --fixed-string "PH8" . 2>/dev/null | LC_ALL=C sort || true
  echo ""

  echo "=== CANDIDATE EVIDENCE PACKS ==="
  echo "--- evidence_output top-level"
  if [ -d "evidence_output" ]; then
    ls -la "evidence_output" | sed -n '1,200p'
  else
    echo "MISSING_DIR=evidence_output"
  fi
  echo ""

  echo "--- evidence_output PH8-like packs"
  if [ -d "evidence_output" ]; then
    find "evidence_output" -maxdepth 3 -type d \
      \( -iname "*PH8*" -o -iname "*PH-8*" -o -iname "*PHASE8*" \) \
      -print | LC_ALL=C sort || true
  fi
  echo ""

  echo "=== EXPECTED PH8 INPUTS (WHAT WE LOOK FOR) ==="
  echo "Expected artifacts (any of these):"
  echo " - docs/PH8/* or PH8_PACK_SUMMARY.md"
  echo " - scripts/petcare_ph8_*.sh"
  echo " - evidence_output/PETCARE-PH8-*/.../MANIFEST.json"
  echo " - Notion-ready checklist in repo (markdown)"
  echo ""

  echo "=== MISSING INPUTS (DERIVED) ==="
  missing=0
  if ! find . -type f -maxdepth 6 \( -iname "*ph8*" -o -path "*PH8*" \) -print | grep -q .; then
    echo "MISSING=PH8 file artifacts (no ph8-named files found)"
    missing=$((missing+1))
  fi
  if [ ! -d "evidence_output" ]; then
    echo "MISSING=evidence_output directory"
    missing=$((missing+1))
  else
    if ! find "evidence_output" -maxdepth 4 -type f -name "MANIFEST.json" | grep -qi "PH8"; then
      echo "MISSING=PH8 closure MANIFEST.json under evidence_output"
      missing=$((missing+1))
    fi
  fi
  echo "missing_count=${missing}"
  echo ""

  echo "=== NEXT ACTION (AUTO) ==="
  echo "If PH8 artifacts are missing, create a PH8 baseline plan doc:"
  echo " - docs/PH8/PH8_PACK_SUMMARY.md"
  echo " - scripts/petcare_ph8_closure_pack.sh"
  echo "Then re-run this scan to confirm presence."
} | tee "${OUT}/ph8_scan_report.txt"

LC_ALL=C sed -n '1,260p' "${OUT}/ph8_scan_report.txt" > "${OUT}/ph8_scan_report_head.txt"

find "${OUT}" -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 > "${OUT}/sha256.txt"

echo "DONE"
echo "OUT=${OUT}"
