#!/usr/bin/env bash
set -euo pipefail

echo "DF26 — FEDERATED CONTROL VALIDATION"

REQUIRED_FILES=(
"FEDERATED_GOVERNANCE_MODEL.md"
"INTEROPERABILITY_CONTRACT_REGISTRY.md"
"POLICY_VERSION_CONTROL.md"
"FEDERATED_EVIDENCE_MODEL.md"
)

for f in "${REQUIRED_FILES[@]}"; do
  if [[ ! -f "petcare_execution/PHASE_2/DF26_PORTFOLIO_FEDERATION/$f" ]]; then
    echo "MISSING: $f"
    exit 1
  fi
done

echo "DF26 VALIDATION PASSED"
