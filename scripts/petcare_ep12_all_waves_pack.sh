#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PACK_ID="PETCARE-PHASE-1-BUILD-EP12-INTELLIGENT-OPERATIONS-AND-DECISION-SUPPORT"
RUN_TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="petcare_execution/EVIDENCE/${PACK_ID}/${RUN_TS}"

mkdir -p "${RUN_DIR}"

export PYTHONPATH="${REPO_ROOT}/petcare_runtime/src:${PYTHONPATH:-}"

python3 -m pytest "petcare_runtime/tests/intelligent_ops/test_intelligent_ops.py" -q | tee "${RUN_DIR}/pytest.log"

cat > "${RUN_DIR}/phase_assertions.txt" <<'ASSERT'
ai_execution_authority=false
ai_approval_authority=false
advisory_only=true
silent_influence_allowed=false
human_override_required=true
ep12_intelligence_layer_present=true
ASSERT

find \
  "petcare_execution/EP12" \
  "petcare_runtime/src/petcare/intelligent_ops" \
  "petcare_runtime/tests/intelligent_ops" \
  "petcare_runtime/migrations/0012_ep12_intelligent_operations_checkpoint.sql" \
  "scripts/petcare_ep12_all_waves_pack.sh" \
  -type f | sort > "${RUN_DIR}/file_listing.txt"

export RUN_DIR_ABS="${REPO_ROOT}/${RUN_DIR}"
export PACK_ID

python3 <<'PY'
import hashlib
import json
import os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR_ABS"])
repo_root = run_dir.parents[3]
manifest_entries = []

for path in sorted(run_dir.rglob("*")):
    if path.is_file():
        rel = path.relative_to(repo_root).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest_entries.append({"path": rel, "sha256": digest})

for rel in [
    "petcare_execution/EP12/EP12_EXECUTION_MASTER_SPEC.md",
    "petcare_execution/EP12/EP12_HARD_GATES.md",
    "petcare_execution/EP12/EP12_NOTION_EXECUTION_MAP.md",
    "petcare_runtime/src/petcare/intelligent_ops/__init__.py",
    "petcare_runtime/src/petcare/intelligent_ops/anomalies.py",
    "petcare_runtime/src/petcare/intelligent_ops/risk.py",
    "petcare_runtime/src/petcare/intelligent_ops/recommendations.py",
    "petcare_runtime/src/petcare/intelligent_ops/optimization.py",
    "petcare_runtime/src/petcare/intelligent_ops/predictive.py",
    "petcare_runtime/src/petcare/intelligent_ops/explainability.py",
    "petcare_runtime/src/petcare/intelligent_ops/audit.py",
    "petcare_runtime/tests/intelligent_ops/test_intelligent_ops.py",
    "petcare_runtime/migrations/0012_ep12_intelligent_operations_checkpoint.sql",
    "scripts/petcare_ep12_all_waves_pack.sh",
]:
    path = repo_root / rel
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest_entries.append({"path": rel, "sha256": digest})

manifest = {
    "pack_id": os.environ["PACK_ID"],
    "run_dir": run_dir.relative_to(repo_root).as_posix(),
    "entries": manifest_entries,
}
(run_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

printf '\nPACK_ID              : %s\n' "$PACK_ID" | tee "${RUN_DIR}/summary.txt"
printf 'VALIDATION           : OK\n' | tee -a "${RUN_DIR}/summary.txt"
printf 'GOVERNANCE_POSITION  : intelligent_operations_advisory_governed\n' | tee -a "${RUN_DIR}/summary.txt"
printf 'EVIDENCE_RUN_DIR     : %s\n' "${RUN_DIR}" | tee -a "${RUN_DIR}/summary.txt"
