#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="${REPO}/evidence_output"

KEEP=5
APPLY=0
DRY=0

usage() {
  echo "Usage: $0 [--keep N] [--apply|--dry-run]"
  echo "  --keep N     keep most recent N run directories per pack (default 5)"
  echo "  --apply      delete old runs"
  echo "  --dry-run    print what would be deleted (default)"
}

# Parse args (bash 3.2 compatible)
while [ $# -gt 0 ]; do
  case "$1" in
    --keep)
      shift
      KEEP="${1:-}"
      ;;
    --apply)
      APPLY=1
      ;;
    --dry-run)
      DRY=1
      APPLY=0
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "FAIL: unknown arg: $1"
      usage
      exit 2
      ;;
  esac
  shift || true
done

if [ -z "${KEEP}" ] || ! echo "${KEEP}" | grep -Eq '^[0-9]+$'; then
  echo "FAIL: --keep must be an integer"
  exit 3
fi

echo "=== EVIDENCE PRUNE ==="
echo "repo=${REPO}"
echo "root=${ROOT}"
echo "keep=${KEEP}"
echo "apply=${APPLY}"

if [ ! -d "${ROOT}" ]; then
  echo "ROOT_MISSING=PASS (no evidence_output yet)"
  echo "RESULT=PASS"
  exit 0
fi

packs=0
kept=0
deleted=0

# Iterate pack directories like evidence_output/PETCARE-PHxx-*/...
find "${ROOT}" -maxdepth 1 -mindepth 1 -type d -print | LC_ALL=C sort | while IFS= read -r pack_dir; do
  packs=$((packs + 1))

  # Collect run dirs under this pack dir that look like timestamps
  # We'll sort newest first (lexicographic works for YYYYMMDDTHHMMSSZ)
  runs_tmp="${REPO}/.tmp_evidence_prune_runs.$$"
  rm -f "${runs_tmp}"
  find "${pack_dir}" -maxdepth 1 -mindepth 1 -type d -print \
    | sed 's#/*$##' \
    | LC_ALL=C sort -r \
    > "${runs_tmp}"

  i=0
  while IFS= read -r d; do
    i=$((i + 1))
    if [ "${i}" -le "${KEEP}" ]; then
      echo "KEEP=${d}"
      kept=$((kept + 1))
    else
      echo "DELETE=${d}"
      if [ "${APPLY}" -eq 1 ]; then
        rm -rf "${d}"
      fi
      deleted=$((deleted + 1))
    fi
  done < "${runs_tmp}"

  rm -f "${runs_tmp}"
done

echo ""
echo "NOTE: Counters are best-effort in bash 3.2 subshell loops."
echo "RESULT=PASS (dry-run by default; use --apply to delete)"
exit 0
