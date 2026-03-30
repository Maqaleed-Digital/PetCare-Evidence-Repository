#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=============================================="
echo "PetCare PH4 — Git Hardening Report"
echo "repo_root=${REPO_ROOT}"
echo "timestamp_utc=$(date -u +%Y%m%dT%H%M%SZ)"
echo "=============================================="
echo ""

if git -C "${REPO_ROOT}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "inside_git=true"
  echo "toplevel=$(git -C "${REPO_ROOT}" rev-parse --show-toplevel)"
  echo "branch=$(git -C "${REPO_ROOT}" branch --show-current 2>/dev/null || true)"
  echo "head=$(git -C "${REPO_ROOT}" log -1 --format='%h %s' 2>/dev/null || true)"
else
  echo "inside_git=false"
fi

echo ""
echo "Recommended ignore entries (apply at git toplevel if needed):"
cat <<'TXT'
petcare_execution/.venv/
petcare_execution/evidence_output/
petcare_execution/__pycache__/
petcare_execution/.DS_Store
petcare_execution/*.pyc
TXT

echo ""
echo "No changes made."
