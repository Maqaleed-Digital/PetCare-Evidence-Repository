#!/usr/bin/env bash
set -euo pipefail

REPO="/Users/waheebmahmoud/dev/petcare-evidence-repository"
cd "$REPO"

python3 "$REPO/petcare_execution/scripts/petcare_executive_portfolio_steady_state_visibility.py"
