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

require_file "petcare_execution/INFRASTRUCTURE/EXECUTIVE_SERVICE_GOVERNANCE_MODEL.md"
require_file "petcare_execution/INFRASTRUCTURE/QUARTERLY_OPERATING_REVIEW_PACK.md"
require_file "petcare_execution/INFRASTRUCTURE/SERVICE_PORTFOLIO_HEALTH_MODEL.md"
require_file "petcare_execution/INFRASTRUCTURE/STRATEGIC_RISK_AND_DEPENDENCY_GOVERNANCE.md"
require_file "petcare_execution/INFRASTRUCTURE/CLINIC_EXPANSION_READINESS_GOVERNANCE.md"
require_file "petcare_execution/INFRASTRUCTURE/PARTNER_PERFORMANCE_GOVERNANCE.md"
require_file "petcare_execution/INFRASTRUCTURE/SERVICE_INVESTMENT_PRIORITIZATION_MODEL.md"
require_file "petcare_execution/INFRASTRUCTURE/ANNUAL_OPERATING_PLAN_LINKAGE.md"
require_file "petcare_execution/INFRASTRUCTURE/BAU_TO_SCALE_TRANSITION_CONTROL.md"
require_file "scripts/petcare_executive_governance_validate.sh"
require_file "scripts/petcare_executive_governance_manifest.sh"

require_grep "petcare_executive_service_governance_active" "petcare_execution/INFRASTRUCTURE/EXECUTIVE_SERVICE_GOVERNANCE_MODEL.md"
require_grep "quarter" "petcare_execution/INFRASTRUCTURE/QUARTERLY_OPERATING_REVIEW_PACK.md"
require_grep "executive_attention_required" "petcare_execution/INFRASTRUCTURE/SERVICE_PORTFOLIO_HEALTH_MODEL.md"
require_grep "dependency_reference" "petcare_execution/INFRASTRUCTURE/STRATEGIC_RISK_AND_DEPENDENCY_GOVERNANCE.md"
require_grep "conditionally_ready" "petcare_execution/INFRASTRUCTURE/CLINIC_EXPANSION_READINESS_GOVERNANCE.md"
require_grep "SLA adherence" "petcare_execution/INFRASTRUCTURE/PARTNER_PERFORMANCE_GOVERNANCE.md"
require_grep "immediate" "petcare_execution/INFRASTRUCTURE/SERVICE_INVESTMENT_PRIORITIZATION_MODEL.md"
require_grep "quarterly operating review outputs must feed annual planning" "petcare_execution/INFRASTRUCTURE/ANNUAL_OPERATING_PLAN_LINKAGE.md"
require_grep "petcare_executive_service_governance_active" "petcare_execution/INFRASTRUCTURE/BAU_TO_SCALE_TRANSITION_CONTROL.md"

if grep -R -n -E '(AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z\-_]{20,}|-----BEGIN|postgres://[^[:space:]]+|password[[:space:]]*=|secret[[:space:]]*=|token[[:space:]]*=)' \
  "petcare_execution/INFRASTRUCTURE" "scripts" \
  --exclude="*.png" --exclude="*.jpg" --exclude="*.jpeg" --exclude="*.gif" --exclude="*.svg" --exclude="*.lock" \
  --exclude="*_validate.sh" \
  > /tmp/petcare_executive_governance_secret_scan.txt; then
  cat /tmp/petcare_executive_governance_secret_scan.txt >&2
  fail "potential secret-like literal detected"
fi

echo "VALIDATION_OK: PETCARE-EXECUTIVE-OPERATING-SYSTEM-AND-PORTFOLIO-SERVICE-GOVERNANCE"
