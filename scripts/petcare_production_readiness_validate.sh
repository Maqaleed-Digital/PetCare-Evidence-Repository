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

require_file "petcare_execution/INFRASTRUCTURE/PRODUCTION_ENVIRONMENT_VARIABLE_CONTRACT.md"
require_file "petcare_execution/INFRASTRUCTURE/PRODUCTION_DEPLOYMENT_RUNBOOK.md"
require_file "petcare_execution/INFRASTRUCTURE/PRODUCTION_ROLLBACK_RUNBOOK.md"
require_file "petcare_execution/INFRASTRUCTURE/BREAK_GLASS_ACCESS_PROCEDURE.md"
require_file "petcare_execution/INFRASTRUCTURE/RELEASE_APPROVAL_WORKFLOW.md"
require_file "petcare_execution/INFRASTRUCTURE/GO_LIVE_VALIDATION_GATE.md"
require_file "petcare_execution/INFRASTRUCTURE/POST_DEPLOY_VERIFICATION_PACK.md"
require_file "scripts/petcare_production_readiness_validate.sh"
require_file "scripts/petcare_production_readiness_manifest.sh"

require_grep "petcare_production_environment_ready" "petcare_execution/INFRASTRUCTURE/PRODUCTION_ENVIRONMENT_VARIABLE_CONTRACT.md"
require_grep "Deployment Sequence" "petcare_execution/INFRASTRUCTURE/PRODUCTION_DEPLOYMENT_RUNBOOK.md"
require_grep "Rollback Triggers" "petcare_execution/INFRASTRUCTURE/PRODUCTION_ROLLBACK_RUNBOOK.md"
require_grep "time-bounded access" "petcare_execution/INFRASTRUCTURE/BREAK_GLASS_ACCESS_PROCEDURE.md"
require_grep "no production self-approval" "petcare_execution/INFRASTRUCTURE/RELEASE_APPROVAL_WORKFLOW.md"
require_grep "Go-live gate passes only if" "petcare_execution/INFRASTRUCTURE/GO_LIVE_VALIDATION_GATE.md"
require_grep "Production release is considered verified" "petcare_execution/INFRASTRUCTURE/POST_DEPLOY_VERIFICATION_PACK.md"

if grep -R -n -E '(AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z\-_]{20,}|-----BEGIN|postgres://[^[:space:]]+|password[[:space:]]*=|secret[[:space:]]*=|token[[:space:]]*=)' \
  "petcare_execution/INFRASTRUCTURE" "scripts" \
  --exclude="*.png" --exclude="*.jpg" --exclude="*.jpeg" --exclude="*.gif" --exclude="*.svg" --exclude="*.lock" \
  --exclude="*_validate.sh" \
  | grep -v 'real secret values must never be committed' \
  | grep -v 'no secret values present in tracked files' \
  | grep -v 'AI_PROVIDER_KEY_REF' \
  | grep -v 'ALERT_ROUTING_KEY_REF' \
  | grep -v 'SESSION_SIGNING_KEY_REF' \
  | grep -v 'KMS_KEY_REF' \
  > /tmp/petcare_production_readiness_secret_scan.txt; then
  cat /tmp/petcare_production_readiness_secret_scan.txt >&2
  fail "potential secret-like literal detected"
fi

echo "VALIDATION_OK: PETCARE-PRODUCTION-ENVIRONMENT-READINESS-AND-DEPLOYMENT-CONTROLS"
