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

require_file "petcare_execution/INFRASTRUCTURE/SOVEREIGN_NATIONAL_CONTROL_MODEL.md"
require_file "petcare_execution/INFRASTRUCTURE/BOARD_LEVEL_NATIONAL_SERVICE_OVERSIGHT_PACK.md"
require_file "petcare_execution/INFRASTRUCTURE/ENTERPRISE_GOVERNANCE_MATURITY_SCORECARD.md"
require_file "petcare_execution/INFRASTRUCTURE/NATIONAL_RESILIENCE_AND_CONTINUITY_GOVERNANCE.md"
require_file "petcare_execution/INFRASTRUCTURE/REGULATOR_AND_COMPLIANCE_OVERSIGHT_PACK.md"
require_file "petcare_execution/INFRASTRUCTURE/NATIONAL_AI_AND_AUDIT_ASSURANCE_REVIEW.md"
require_file "petcare_execution/INFRASTRUCTURE/STRATEGIC_CAPITAL_AND_SCALE_INVESTMENT_GOVERNANCE.md"
require_file "petcare_execution/INFRASTRUCTURE/PLATFORM_MATURITY_TRANSITION_CLOSEOUT.md"
require_file "scripts/petcare_sovereign_maturity_validate.sh"
require_file "scripts/petcare_sovereign_maturity_manifest.sh"

require_grep "petcare_sovereign_platform_maturity_governed" "petcare_execution/INFRASTRUCTURE/SOVEREIGN_NATIONAL_CONTROL_MODEL.md"
require_grep "next review date" "petcare_execution/INFRASTRUCTURE/BOARD_LEVEL_NATIONAL_SERVICE_OVERSIGHT_PACK.md"
require_grep "sovereign_mature" "petcare_execution/INFRASTRUCTURE/ENTERPRISE_GOVERNANCE_MATURITY_SCORECARD.md"
require_grep "continuity posture" "petcare_execution/INFRASTRUCTURE/NATIONAL_RESILIENCE_AND_CONTINUITY_GOVERNANCE.md"
require_grep "KSA data residency posture" "petcare_execution/INFRASTRUCTURE/REGULATOR_AND_COMPLIANCE_OVERSIGHT_PACK.md"
require_grep "assistive-only boundary must remain preserved" "petcare_execution/INFRASTRUCTURE/NATIONAL_AI_AND_AUDIT_ASSURANCE_REVIEW.md"
require_grep "approve_now" "petcare_execution/INFRASTRUCTURE/STRATEGIC_CAPITAL_AND_SCALE_INVESTMENT_GOVERNANCE.md"
require_grep "petcare_sovereign_platform_maturity_governed" "petcare_execution/INFRASTRUCTURE/PLATFORM_MATURITY_TRANSITION_CLOSEOUT.md"

if grep -R -n -E '(AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z\-_]{20,}|-----BEGIN|postgres://[^[:space:]]+|password[[:space:]]*=|secret[[:space:]]*=|token[[:space:]]*=)' \
  "petcare_execution/INFRASTRUCTURE" "scripts" \
  --exclude="*.png" --exclude="*.jpg" --exclude="*.jpeg" --exclude="*.gif" --exclude="*.svg" --exclude="*.lock" \
  --exclude="*_validate.sh" \
  > /tmp/petcare_sovereign_maturity_secret_scan.txt; then
  cat /tmp/petcare_sovereign_maturity_secret_scan.txt >&2
  fail "potential secret-like literal detected"
fi

echo "VALIDATION_OK: PETCARE-SOVEREIGN-PLATFORM-MATURITY-AND-BOARD-LEVEL-NATIONAL-CONTROL-GOVERNANCE"
