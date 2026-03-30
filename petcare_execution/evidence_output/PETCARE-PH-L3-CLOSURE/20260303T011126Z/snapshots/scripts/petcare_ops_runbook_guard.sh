#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

req_files=(
  "docs/PRODUCTION_RUNBOOK.md"
  "docs/INCIDENT_RESPONSE_PLAYBOOK.md"
)

for f in "${req_files[@]}"; do
  if [ ! -f "${REPO_ROOT}/${f}" ]; then
    echo "FATAL: missing required doc: ${f}"
    exit 3
  fi
done

must_have_prod=(
  "^# PetCare Production Runbook"
  "^\*\*Document ID:\*\*"
  "^## 3\. Roles & On-Call Escalation"
  "^## 6\. Rollback Procedure"
)

must_have_irp=(
  "^# PetCare Incident Response Playbook"
  "^\*\*Document ID:\*\*"
  "^## 1\. Severity Definitions"
  "^## 3\. First 15 Minutes Checklist"
  "^## 4\. Communications Templates"
)

for pat in "${must_have_prod[@]}"; do
  if ! grep -qE "${pat}" "${REPO_ROOT}/docs/PRODUCTION_RUNBOOK.md"; then
    echo "FATAL: PRODUCTION_RUNBOOK missing pattern: ${pat}"
    exit 31
  fi
done

for pat in "${must_have_irp[@]}"; do
  if ! grep -qE "${pat}" "${REPO_ROOT}/docs/INCIDENT_RESPONSE_PLAYBOOK.md"; then
    echo "FATAL: INCIDENT_RESPONSE_PLAYBOOK missing pattern: ${pat}"
    exit 32
  fi
done

echo "OK: PH-L3 runbook guard PASS"
