#!/usr/bin/env bash
set -euo pipefail

echo "PH6 PILOT ACTIVATION START"

if [[ "$PILOT_MAX_CLINICS" -gt 2 ]]; then
  echo "FAIL: Clinic limit exceeded"
  exit 1
fi

if [[ "$PILOT_MAX_VETS" -gt 5 ]]; then
  echo "FAIL: Vet limit exceeded"
  exit 1
fi

if [[ "$GOVERNANCE_APPROVAL" != "approved" ]]; then
  echo "FAIL: Governance approval missing"
  exit 1
fi

echo "PASS: Governance validated"
