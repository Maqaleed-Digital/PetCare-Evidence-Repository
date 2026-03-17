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

require_file "petcare_execution/INFRASTRUCTURE/NATIONAL_SERVICE_NETWORK_GOVERNANCE_MODEL.md"
require_file "petcare_execution/INFRASTRUCTURE/REGIONAL_OPERATING_UNIT_GOVERNANCE.md"
require_file "petcare_execution/INFRASTRUCTURE/CROSS_REGION_SERVICE_CONSISTENCY_CONTROLS.md"
require_file "petcare_execution/INFRASTRUCTURE/NATIONAL_PARTNER_NETWORK_GOVERNANCE.md"
require_file "petcare_execution/INFRASTRUCTURE/REGIONAL_PERFORMANCE_REVIEW_PACK.md"
require_file "petcare_execution/INFRASTRUCTURE/INTER_CLINIC_ESCALATION_AND_REFERRAL_GOVERNANCE.md"
require_file "petcare_execution/INFRASTRUCTURE/NATIONAL_CAPACITY_BALANCING_MODEL.md"
require_file "petcare_execution/INFRASTRUCTURE/REGIONAL_RISK_AND_RESILIENCE_GOVERNANCE.md"
require_file "petcare_execution/INFRASTRUCTURE/SCALE_TO_NETWORK_TRANSITION_CLOSEOUT.md"
require_file "scripts/petcare_national_network_validate.sh"
require_file "scripts/petcare_national_network_manifest.sh"

require_grep "petcare_national_service_network_governed" "petcare_execution/INFRASTRUCTURE/NATIONAL_SERVICE_NETWORK_GOVERNANCE_MODEL.md"
require_grep "region_id" "petcare_execution/INFRASTRUCTURE/REGIONAL_OPERATING_UNIT_GOVERNANCE.md"
require_grep "intervention_required" "petcare_execution/INFRASTRUCTURE/CROSS_REGION_SERVICE_CONSISTENCY_CONTROLS.md"
require_grep "concentration risk" "petcare_execution/INFRASTRUCTURE/NATIONAL_PARTNER_NETWORK_GOVERNANCE.md"
require_grep "current source-of-truth commit" "petcare_execution/INFRASTRUCTURE/REGIONAL_PERFORMANCE_REVIEW_PACK.md"
require_grep "auditable" "petcare_execution/INFRASTRUCTURE/INTER_CLINIC_ESCALATION_AND_REFERRAL_GOVERNANCE.md"
require_grep "imbalance risks" "petcare_execution/INFRASTRUCTURE/NATIONAL_CAPACITY_BALANCING_MODEL.md"
require_grep "resilience posture" "petcare_execution/INFRASTRUCTURE/REGIONAL_RISK_AND_RESILIENCE_GOVERNANCE.md"
require_grep "petcare_national_service_network_governed" "petcare_execution/INFRASTRUCTURE/SCALE_TO_NETWORK_TRANSITION_CLOSEOUT.md"

if grep -R -n -E '(AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z\-_]{20,}|-----BEGIN|postgres://[^[:space:]]+|password[[:space:]]*=|secret[[:space:]]*=|token[[:space:]]*=)' \
  "petcare_execution/INFRASTRUCTURE" "scripts" \
  --exclude="*.png" --exclude="*.jpg" --exclude="*.jpeg" --exclude="*.gif" --exclude="*.svg" --exclude="*.lock" \
  --exclude="*_validate.sh" \
  > /tmp/petcare_national_network_secret_scan.txt; then
  cat /tmp/petcare_national_network_secret_scan.txt >&2
  fail "potential secret-like literal detected"
fi

echo "VALIDATION_OK: PETCARE-NATIONAL-SERVICE-NETWORK-AND-REGIONAL-OPERATING-GOVERNANCE"
