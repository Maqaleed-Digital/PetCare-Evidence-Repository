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

require_file "petcare_execution/INFRASTRUCTURE/LIVE_PRODUCTION_DEPLOYMENT_EXECUTION_RECORD.md"
require_file "petcare_execution/INFRASTRUCTURE/LIVE_RELEASE_REGISTRATION.md"
require_file "petcare_execution/INFRASTRUCTURE/LIVE_HEALTH_VERIFICATION.md"
require_file "petcare_execution/INFRASTRUCTURE/LIVE_AUDIT_PATH_VERIFICATION.md"
require_file "petcare_execution/INFRASTRUCTURE/LIVE_AI_GOVERNANCE_PATH_VERIFICATION.md"
require_file "petcare_execution/INFRASTRUCTURE/LIVE_OBSERVABILITY_VERIFICATION.md"
require_file "petcare_execution/INFRASTRUCTURE/ROLLBACK_DRILL_CONFIRMATION.md"
require_file "petcare_execution/INFRASTRUCTURE/GO_LIVE_CLOSEOUT_EVIDENCE.md"
require_file "scripts/petcare_live_production_validate.sh"
require_file "scripts/petcare_live_production_manifest.sh"

require_grep "petcare_live_production_verified" "petcare_execution/INFRASTRUCTURE/LIVE_PRODUCTION_DEPLOYMENT_EXECUTION_RECORD.md"
require_grep "live_verified" "petcare_execution/INFRASTRUCTURE/LIVE_RELEASE_REGISTRATION.md"
require_grep "Critical Health Checks" "petcare_execution/INFRASTRUCTURE/LIVE_HEALTH_VERIFICATION.md"
require_grep "audit event sample recorded" "petcare_execution/INFRASTRUCTURE/LIVE_AUDIT_PATH_VERIFICATION.md"
require_grep "assistive-only boundary preserved" "petcare_execution/INFRASTRUCTURE/LIVE_AI_GOVERNANCE_PATH_VERIFICATION.md"
require_grep "logs flowing" "petcare_execution/INFRASTRUCTURE/LIVE_OBSERVABILITY_VERIFICATION.md"
require_grep "confirmed" "petcare_execution/INFRASTRUCTURE/ROLLBACK_DRILL_CONFIRMATION.md"
require_grep "petcare_live_production_verified" "petcare_execution/INFRASTRUCTURE/GO_LIVE_CLOSEOUT_EVIDENCE.md"

if grep -R -n -E '(AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z\-_]{20,}|-----BEGIN|postgres://[^[:space:]]+|password[[:space:]]*=|secret[[:space:]]*=|token[[:space:]]*=)' \
  "petcare_execution/INFRASTRUCTURE" "scripts" \
  --exclude="*.png" --exclude="*.jpg" --exclude="*.jpeg" --exclude="*.gif" --exclude="*.svg" --exclude="*.lock" \
  --exclude="*_validate.sh" \
  | grep -v 'no real secret values' \
  | grep -v 'assistive-only boundary preserved' \
  > /tmp/petcare_live_production_secret_scan.txt; then
  cat /tmp/petcare_live_production_secret_scan.txt >&2
  fail "potential secret-like literal detected"
fi

echo "VALIDATION_OK: PETCARE-LIVE-PRODUCTION-DEPLOYMENT-AND-VERIFICATION"
