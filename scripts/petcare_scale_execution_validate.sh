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

require_file "petcare_execution/INFRASTRUCTURE/MULTI_CLINIC_SCALE_GOVERNANCE_MODEL.md"
require_file "petcare_execution/INFRASTRUCTURE/EXPANSION_WAVE_PLANNING_PACK.md"
require_file "petcare_execution/INFRASTRUCTURE/CLINIC_LAUNCH_READINESS_CHECKLIST.md"
require_file "petcare_execution/INFRASTRUCTURE/SCALED_SERVICE_CAPACITY_MODEL.md"
require_file "petcare_execution/INFRASTRUCTURE/REGIONAL_PARTNER_ONBOARDING_GOVERNANCE.md"
require_file "petcare_execution/INFRASTRUCTURE/EXPANSION_RISK_REGISTER.md"
require_file "petcare_execution/INFRASTRUCTURE/ROLLOUT_SEQUENCING_AND_DEPENDENCY_CONTROL.md"
require_file "petcare_execution/INFRASTRUCTURE/POST_EXPANSION_STABILIZATION_GOVERNANCE.md"
require_file "petcare_execution/INFRASTRUCTURE/EXECUTIVE_SCALE_REVIEW_PACK.md"
require_file "scripts/petcare_scale_execution_validate.sh"
require_file "scripts/petcare_scale_execution_manifest.sh"

require_grep "petcare_multi_clinic_scale_execution_governed" "petcare_execution/INFRASTRUCTURE/MULTI_CLINIC_SCALE_GOVERNANCE_MODEL.md"
require_grep "wave_id" "petcare_execution/INFRASTRUCTURE/EXPANSION_WAVE_PLANNING_PACK.md"
require_grep "conditionally_ready" "petcare_execution/INFRASTRUCTURE/CLINIC_LAUNCH_READINESS_CHECKLIST.md"
require_grep "forecast by wave" "petcare_execution/INFRASTRUCTURE/SCALED_SERVICE_CAPACITY_MODEL.md"
require_grep "no regional partner goes live without readiness result" "petcare_execution/INFRASTRUCTURE/REGIONAL_PARTNER_ONBOARDING_GOVERNANCE.md"
require_grep "expansion_risk_id" "petcare_execution/INFRASTRUCTURE/EXPANSION_RISK_REGISTER.md"
require_grep "stabilization checkpoint" "petcare_execution/INFRASTRUCTURE/ROLLOUT_SEQUENCING_AND_DEPENDENCY_CONTROL.md"
require_grep "named stabilization window" "petcare_execution/INFRASTRUCTURE/POST_EXPANSION_STABILIZATION_GOVERNANCE.md"
require_grep "next wave recommendation" "petcare_execution/INFRASTRUCTURE/EXECUTIVE_SCALE_REVIEW_PACK.md"

if grep -R -n -E '(AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z\-_]{20,}|-----BEGIN|postgres://[^[:space:]]+|password[[:space:]]*=|secret[[:space:]]*=|token[[:space:]]*=)' \
  "petcare_execution/INFRASTRUCTURE" "scripts" \
  --exclude="*.png" --exclude="*.jpg" --exclude="*.jpeg" --exclude="*.gif" --exclude="*.svg" --exclude="*.lock" \
  --exclude="*_validate.sh" \
  > /tmp/petcare_scale_execution_secret_scan.txt; then
  cat /tmp/petcare_scale_execution_secret_scan.txt >&2
  fail "potential secret-like literal detected"
fi

echo "VALIDATION_OK: PETCARE-SCALE-EXPANSION-READINESS-AND-MULTI-CLINIC-EXECUTION-GOVERNANCE"
