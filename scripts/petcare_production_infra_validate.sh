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

require_file "petcare_execution/INFRASTRUCTURE/PRODUCTION_ARCHITECTURE_BLUEPRINT.md"
require_file "petcare_execution/INFRASTRUCTURE/CLOUD_DEPLOYMENT_MODEL.md"
require_file "petcare_execution/INFRASTRUCTURE/NETWORK_TOPOLOGY.md"
require_file "petcare_execution/INFRASTRUCTURE/SECURITY_MODEL.md"
require_file "petcare_execution/INFRASTRUCTURE/OBSERVABILITY_STACK.md"
require_file "petcare_execution/INFRASTRUCTURE/SECRETS_MANAGEMENT.md"
require_file "petcare_execution/INFRASTRUCTURE/CI_CD_PIPELINE.md"
require_file "scripts/petcare_production_infra_validate.sh"
require_file "scripts/petcare_production_infra_manifest.sh"

require_grep "petcare_production_environment_ready" "petcare_execution/INFRASTRUCTURE/PRODUCTION_ARCHITECTURE_BLUEPRINT.md"
require_grep "KSA" "petcare_execution/INFRASTRUCTURE/CLOUD_DEPLOYMENT_MODEL.md"
require_grep "deny all by default" "petcare_execution/INFRASTRUCTURE/NETWORK_TOPOLOGY.md"
require_grep "zero trust" "petcare_execution/INFRASTRUCTURE/SECURITY_MODEL.md"
require_grep "logs" "petcare_execution/INFRASTRUCTURE/OBSERVABILITY_STACK.md"
require_grep "production secrets are never committed" "petcare_execution/INFRASTRUCTURE/SECRETS_MANAGEMENT.md"
require_grep "deployment validation" "petcare_execution/INFRASTRUCTURE/CI_CD_PIPELINE.md"

if grep -R -n -E '(AKIA|AIza|-----BEGIN|postgres://|password=|secret=|token=)' \
  "petcare_execution/INFRASTRUCTURE" "scripts" \
  --exclude="*.pyc" \
  --exclude="*.png" \
  --exclude="*.jpg" \
  --exclude="*.jpeg" \
  --exclude="*.gif" \
  --exclude="*.svg" \
  --exclude="*.lock" \
  --exclude="petcare_production_infra_validate.sh" \
  | grep -v 'secret values' \
  | grep -v 'secret literals appear' \
  | grep -v 'production secrets are never committed' \
  | grep -v 'secret placeholders' \
  > /tmp/petcare_infra_secret_scan.txt; then
  cat /tmp/petcare_infra_secret_scan.txt >&2
  fail "potential secret-like literal detected"
fi

echo "VALIDATION_OK: PETCARE-PRODUCTION-INFRASTRUCTURE-DEPLOYMENT"
