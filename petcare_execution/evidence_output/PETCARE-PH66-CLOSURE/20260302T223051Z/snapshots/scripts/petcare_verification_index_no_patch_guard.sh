#!/usr/bin/env bash
set -euo pipefail

# PH66 guard: CI must not invoke deprecated patch tool.
# Fails if petcare_ci_gates.sh (or any workflow script) references patch_quorum.
# Excludes: historical closure pack scripts (petcare_ph*_closure_pack.sh) which are
# archival evidence and legitimately reference old tooling; and this guard itself.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
needle="petcare_verification_index_patch_quorum.py"

echo "=== PH66 NO-PATCH GUARD ==="
echo "repo_root=${REPO_ROOT}"

# Search only scripts + workflows (scope-limited, deterministic).
# Exclude: closure pack scripts (archival evidence, not active CI tooling)
# Exclude: this guard script (self-reference in needle variable assignment)
hits="$(git -C "${REPO_ROOT}" grep -n "${needle}" -- \
  "scripts" ".github/workflows" 2>/dev/null \
  | grep -v "petcare_ph[0-9][0-9]*_closure_pack\.sh:" \
  | grep -v "petcare_verification_index_no_patch_guard\.sh:" \
  || true)"

if [ -n "${hits}" ]; then
  echo "FAIL: deprecated patch tool referenced in active scripts/workflows:"
  echo "${hits}"
  exit 66
fi

echo "OK: no references to deprecated patch tool in active scripts/workflows"
