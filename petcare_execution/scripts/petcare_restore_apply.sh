#!/usr/bin/env bash
set -euo pipefail

# Applies a backup bundle zip into a clean restore root.
# No guessing: refuses if restore target exists and is non-empty.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

BACKUP_ZIP="${BACKUP_ZIP:-}"
RESTORE_ROOT="${RESTORE_ROOT:-}"

if [ -z "${BACKUP_ZIP}" ] || [ -z "${RESTORE_ROOT}" ]; then
  echo "FATAL: BACKUP_ZIP and RESTORE_ROOT are required."
  echo "Example: BACKUP_ZIP=/path/to/...zip RESTORE_ROOT=/tmp/petcare_restore_root"
  exit 3
fi

if [ ! -f "${BACKUP_ZIP}" ]; then
  echo "FATAL: backup zip not found: ${BACKUP_ZIP}"
  exit 3
fi

mkdir -p "${RESTORE_ROOT}"

# Must be empty (no guessing)
if [ -n "$(ls -A "${RESTORE_ROOT}" 2>/dev/null || true)" ]; then
  echo "FATAL: RESTORE_ROOT is not empty: ${RESTORE_ROOT}"
  exit 3
fi

unzip -q "${BACKUP_ZIP}" -d "${RESTORE_ROOT}"

echo "OK restore applied"
echo "restore_root=${RESTORE_ROOT}"
