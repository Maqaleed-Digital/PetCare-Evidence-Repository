#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="${REPO}/evidence_output"

KEEP="5"
APPLY="0"

usage() {
  echo "usage: $0 [--keep N] [--apply] [--dry-run]"
  echo "default: --dry-run, --keep 5"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --keep)
      KEEP="${2:-}"
      shift 2
      ;;
    --apply)
      APPLY="1"
      shift
      ;;
    --dry-run)
      APPLY="0"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "FAIL: unknown arg: $1"
      usage
      exit 10
      ;;
  esac
done

echo "=== EVIDENCE PRUNE ==="
echo "repo=${REPO}"
echo "root=${ROOT}"
echo "keep=${KEEP}"
echo "apply=${APPLY}"

if ! printf "%s" "${KEEP}" | grep -Eq '^[0-9]+$'; then
  echo "FAIL: keep must be integer"
  exit 11
fi

if [ ! -d "${ROOT}" ]; then
  echo "EVIDENCE_ROOT_MISSING=PASS (no evidence_output yet)"
  exit 0
fi

# For each pack dir evidence_output/<PACK>/, keep newest N timestamp dirs, delete the rest
# Sort order: timestamps are YYYYMMDDTHHMMSSZ (lexicographically sortable)
deleted=0
kept=0
packs=0

for pack_dir in "${ROOT}"/*; do
  [ -d "${pack_dir}" ] || continue
  pack="$(basename "${pack_dir}")"
  packs=$((packs + 1))

  # timestamp dirs only (ignore zip files at pack root)
  mapfile -t ts_dirs < <(find "${pack_dir}" -maxdepth 1 -type d -name "20*Z" -print | LC_ALL=C sort)

  count="${#ts_dirs[@]}"
  echo ""
  echo "PACK=${pack} runs=${count}"

  if [ "${count}" -le "${KEEP}" ]; then
    echo "PRUNE_SKIPPED=keep_all"
    kept=$((kept + count))
    continue
  fi

  # split: keep last KEEP, delete the rest
  del_count=$((count - KEEP))
  echo "DELETE_CANDIDATES=${del_count}"
  echo "KEEP_LAST=${KEEP}"

  i=0
  for d in "${ts_dirs[@]}"; do
    i=$((i + 1))
    if [ "${i}" -le "${del_count}" ]; then
      echo "DELETE=${d}"
      if [ "${APPLY}" -eq 1 ]; then
        rm -rf "${d}"
      fi
      deleted=$((deleted + 1))
    else
      echo "KEEP=${d}"
      kept=$((kept + 1))
    fi
  done
done

echo ""
echo "PACKS_SCANNED=${packs}"
echo "DIRS_KEPT=${kept}"
echo "DIRS_DELETED=${deleted}"

if [ "${APPLY}" -eq 1 ]; then
  echo "RESULT=PASS (apply)"
else
  echo "RESULT=PASS (dry-run)"
fi

exit 0
