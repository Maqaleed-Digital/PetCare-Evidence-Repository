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

require_file "petcare_execution/INFRASTRUCTURE/ENTERPRISE_NETWORK_ORCHESTRATION_MODEL.md"
require_file "petcare_execution/INFRASTRUCTURE/NATIONAL_COMMAND_CADENCE.md"
require_file "petcare_execution/INFRASTRUCTURE/CROSS_REGION_OPTIMIZATION_GOVERNANCE.md"
require_file "petcare_execution/INFRASTRUCTURE/NATIONAL_REFERRAL_LOAD_BALANCING_GOVERNANCE.md"
require_file "petcare_execution/INFRASTRUCTURE/NETWORK_WIDE_SERVICE_QUALITY_SCORECARD.md"
require_file "petcare_execution/INFRASTRUCTURE/ENTERPRISE_DEPENDENCY_AND_RESILIENCE_CONTROL.md"
require_file "petcare_execution/INFRASTRUCTURE/EXPANSION_OPTIMIZATION_BACKLOG_GOVERNANCE.md"
require_file "petcare_execution/INFRASTRUCTURE/NATIONAL_OPERATING_REVIEW_PACK.md"
require_file "petcare_execution/INFRASTRUCTURE/NETWORK_MATURITY_TRANSITION_CLOSEOUT.md"
require_file "scripts/petcare_enterprise_network_validate.sh"
require_file "scripts/petcare_enterprise_network_manifest.sh"

require_grep "petcare_enterprise_network_orchestration_governed" "petcare_execution/INFRASTRUCTURE/ENTERPRISE_NETWORK_ORCHESTRATION_MODEL.md"
require_grep "cadence_type" "petcare_execution/INFRASTRUCTURE/NATIONAL_COMMAND_CADENCE.md"
require_grep "intervention_required" "petcare_execution/INFRASTRUCTURE/CROSS_REGION_OPTIMIZATION_GOVERNANCE.md"
require_grep "overflow hotspots" "petcare_execution/INFRASTRUCTURE/NATIONAL_REFERRAL_LOAD_BALANCING_GOVERNANCE.md"
require_grep "executive_attention_required" "petcare_execution/INFRASTRUCTURE/NETWORK_WIDE_SERVICE_QUALITY_SCORECARD.md"
require_grep "resilience posture" "petcare_execution/INFRASTRUCTURE/ENTERPRISE_DEPENDENCY_AND_RESILIENCE_CONTROL.md"
require_grep "optimization_id" "petcare_execution/INFRASTRUCTURE/EXPANSION_OPTIMIZATION_BACKLOG_GOVERNANCE.md"
require_grep "next-cycle priorities" "petcare_execution/INFRASTRUCTURE/NATIONAL_OPERATING_REVIEW_PACK.md"
require_grep "petcare_enterprise_network_orchestration_governed" "petcare_execution/INFRASTRUCTURE/NETWORK_MATURITY_TRANSITION_CLOSEOUT.md"

if grep -R -n -E '(AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z\-_]{20,}|-----BEGIN|postgres://[^[:space:]]+|password[[:space:]]*=|secret[[:space:]]*=|token[[:space:]]*=)' \
  "petcare_execution/INFRASTRUCTURE" "scripts" \
  --exclude="*.png" --exclude="*.jpg" --exclude="*.jpeg" --exclude="*.gif" --exclude="*.svg" --exclude="*.lock" \
  --exclude="*_validate.sh" \
  > /tmp/petcare_enterprise_network_secret_scan.txt; then
  cat /tmp/petcare_enterprise_network_secret_scan.txt >&2
  fail "potential secret-like literal detected"
fi

echo "VALIDATION_OK: PETCARE-ENTERPRISE-NETWORK-OPTIMIZATION-AND-NATIONAL-ORCHESTRATION-GOVERNANCE"
