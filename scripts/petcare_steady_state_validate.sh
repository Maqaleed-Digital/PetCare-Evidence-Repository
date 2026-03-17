#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail() {
  echo "VALIDATION_FAIL: $1" >&2
  exit 1
}

require_file() {
  local f="$1"
  [ -f "$f" ] || fail "missing file $f"
}

require_grep() {
  local pattern="$1"
  local file="$2"
  grep -q "$pattern" "$file" || fail "pattern [$pattern] not found in $file"
}

require_file "petcare_execution/INFRASTRUCTURE/STEADY_STATE_OPERATING_MODEL.md"
require_file "petcare_execution/INFRASTRUCTURE/WEEKLY_SERVICE_REVIEW_GOVERNANCE.md"
require_file "petcare_execution/INFRASTRUCTURE/MONTHLY_KPI_SLO_BOARD_PACK.md"
require_file "petcare_execution/INFRASTRUCTURE/PROBLEM_MANAGEMENT_AND_RCA_GOVERNANCE.md"
require_file "petcare_execution/INFRASTRUCTURE/CAPACITY_AND_AVAILABILITY_PLANNING.md"
require_file "petcare_execution/INFRASTRUCTURE/RELEASE_CALENDAR_GOVERNANCE.md"
require_file "petcare_execution/INFRASTRUCTURE/VENDOR_AND_PARTNER_OPERATIONS_REVIEW.md"
require_file "petcare_execution/INFRASTRUCTURE/CONTINUOUS_IMPROVEMENT_BACKLOG_GOVERNANCE.md"
require_file "petcare_execution/INFRASTRUCTURE/HYPERCARE_TO_BAU_TRANSITION_CLOSEOUT.md"
require_file "scripts/petcare_steady_state_validate.sh"
require_file "scripts/petcare_steady_state_manifest.sh"

require_grep "petcare_steady_state_governed_operations_active" "petcare_execution/INFRASTRUCTURE/STEADY_STATE_OPERATING_MODEL.md"
require_grep "review_week" "petcare_execution/INFRASTRUCTURE/WEEKLY_SERVICE_REVIEW_GOVERNANCE.md"
require_grep "audit path continuity trend" "petcare_execution/INFRASTRUCTURE/MONTHLY_KPI_SLO_BOARD_PACK.md"
require_grep "root cause summary" "petcare_execution/INFRASTRUCTURE/PROBLEM_MANAGEMENT_AND_RCA_GOVERNANCE.md"
require_grep "forecast horizon" "petcare_execution/INFRASTRUCTURE/CAPACITY_AND_AVAILABILITY_PLANNING.md"
require_grep "release_window" "petcare_execution/INFRASTRUCTURE/RELEASE_CALENDAR_GOVERNANCE.md"
require_grep "SLA adherence" "petcare_execution/INFRASTRUCTURE/VENDOR_AND_PARTNER_OPERATIONS_REVIEW.md"
require_grep "improvement_id" "petcare_execution/INFRASTRUCTURE/CONTINUOUS_IMPROVEMENT_BACKLOG_GOVERNANCE.md"
require_grep "petcare_steady_state_governed_operations_active" "petcare_execution/INFRASTRUCTURE/HYPERCARE_TO_BAU_TRANSITION_CLOSEOUT.md"

if grep -R -n -E '(AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z\-_]{20,}|-----BEGIN|postgres://[^[:space:]]+|password[[:space:]]*=|secret[[:space:]]*=|token[[:space:]]*=)' \
  "petcare_execution/INFRASTRUCTURE" "scripts" \
  --exclude="*.png" --exclude="*.jpg" --exclude="*.jpeg" --exclude="*.gif" --exclude="*.svg" --exclude="*.lock" \
  --exclude="*_validate.sh" \
  > /tmp/petcare_steady_state_secret_scan.txt; then
  cat /tmp/petcare_steady_state_secret_scan.txt >&2
  fail "potential secret-like literal detected"
fi

echo "VALIDATION_OK: PETCARE-STEADY-STATE-OPERATIONS-AND-CONTINUOUS-IMPROVEMENT-GOVERNANCE"
