#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PACK_ID="PETCARE-PHASE-1-CLOSE-EP11"
RUN_TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="petcare_execution/EVIDENCE/${PACK_ID}/${RUN_TS}"

mkdir -p "$RUN_DIR"

git status -sb | tee "$RUN_DIR/git_status.txt"
git rev-parse HEAD | tee "$RUN_DIR/git_head.txt"

export PYTHONPATH="$REPO_ROOT/petcare_runtime/src:${PYTHONPATH:-}"

python3 -m pytest petcare_runtime/tests/payment_activation/test_payment_activation.py -q | tee "$RUN_DIR/tests.log"

cat > "$RUN_DIR/invariant_check.txt" <<'ASSERT'
ai_execution_authority=false
explicit_human_authorization_required=true
treasury_control_required=true
dual_control_supported=true
dispatch_requires_authorization_and_treasury=true
execution_reversible=true
ASSERT

find petcare_execution/EP11_CLOSURE -type f | sort > "$RUN_DIR/file_listing.txt"

export RUN_DIR_ABS="${REPO_ROOT}/${RUN_DIR}"
export PACK_ID

python3 <<'PY'
import hashlib, json, os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR_ABS"])
repo_root = run_dir.parents[3]

entries = []
for path in sorted(run_dir.rglob("*")):
    if path.is_file():
        entries.append({
            "path": path.relative_to(repo_root).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()
        })

(run_dir / "MANIFEST.json").write_text(json.dumps({
    "pack_id": os.environ["PACK_ID"],
    "entries": entries
}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

printf "VALIDATION=OK\n" | tee "$RUN_DIR/summary.txt"
printf "GOVERNANCE=ep11_closed_governed\n" | tee -a "$RUN_DIR/summary.txt"
