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

require_file "petcare_execution/INFRASTRUCTURE/HYPERCARE_OPERATING_WINDOW.md"
require_file "petcare_execution/INFRASTRUCTURE/INCIDENT_AND_ESCALATION_GOVERNANCE.md"
require_file "petcare_execution/INFRASTRUCTURE/PRODUCTION_KPI_SLO_CONTROL_PACK.md"
require_file "petcare_execution/INFRASTRUCTURE/DAILY_OPERATIONAL_REVIEW_TEMPLATE.md"
require_file "petcare_execution/INFRASTRUCTURE/LIVE_ISSUE_TRIAGE_AND_SEVERITY_MODEL.md"
require_file "petcare_execution/INFRASTRUCTURE/CHANGE_FREEZE_AND_EMERGENCY_CHANGE_RULES.md"
require_file "petcare_execution/INFRASTRUCTURE/POST_GO_LIVE_REPORTING_PACK.md"
require_file "petcare_execution/INFRASTRUCTURE/HYPERCARE_CLOSEOUT_CRITERIA.md"
require_file "scripts/petcare_hypercare_validate.sh"
require_file "scripts/petcare_hypercare_manifest.sh"

require_grep "petcare_hypercare_governed_operations_active" "petcare_execution/INFRASTRUCTURE/HYPERCARE_OPERATING_WINDOW.md"
require_grep "Sev-1" "petcare_execution/INFRASTRUCTURE/INCIDENT_AND_ESCALATION_GOVERNANCE.md"
require_grep "audit path success rate" "petcare_execution/INFRASTRUCTURE/PRODUCTION_KPI_SLO_CONTROL_PACK.md"
require_grep "source_of_truth_commit" "petcare_execution/INFRASTRUCTURE/DAILY_OPERATIONAL_REVIEW_TEMPLATE.md"
require_grep "Every live issue must receive an explicit severity and owner" "petcare_execution/INFRASTRUCTURE/LIVE_ISSUE_TRIAGE_AND_SEVERITY_MODEL.md"
require_grep "emergency change requires named approver" "petcare_execution/INFRASTRUCTURE/CHANGE_FREEZE_AND_EMERGENCY_CHANGE_RULES.md"
require_grep "incident summary by severity" "petcare_execution/INFRASTRUCTURE/POST_GO_LIVE_REPORTING_PACK.md"
require_grep "petcare_hypercare_governed_operations_active" "petcare_execution/INFRASTRUCTURE/HYPERCARE_CLOSEOUT_CRITERIA.md"

if grep -R -n -E '(AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z\-_]{20,}|-----BEGIN|postgres://[^[:space:]]+|password[[:space:]]*=|secret[[:space:]]*=|token[[:space:]]*=)' \
  "petcare_execution/INFRASTRUCTURE" "scripts" \
  --exclude="*.png" --exclude="*.jpg" --exclude="*.jpeg" --exclude="*.gif" --exclude="*.svg" --exclude="*.lock" \
  --exclude="*_validate.sh" \
  > /tmp/petcare_hypercare_secret_scan.txt; then
  cat /tmp/petcare_hypercare_secret_scan.txt >&2
  fail "potential secret-like literal detected"
fi

echo "VALIDATION_OK: PETCARE-PRODUCTION-HYPERCARE-AND-OPERATIONS-GOVERNANCE"
