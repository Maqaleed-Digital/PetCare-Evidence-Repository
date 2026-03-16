#!/usr/bin/env bash
set -euo pipefail

REPO="/Users/waheebmahmoud/dev/petcare-evidence-repository"
cd "$REPO"

python3 "$REPO/petcare_execution/scripts/petcare_clinic_wave_hypercare_governance.py"
