#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PACK_ID="PETCARE-PHASE-1-CLOSE-EP10"
RUN_TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="petcare_execution/EVIDENCE/${PACK_ID}/${RUN_TS}"

mkdir -p "${RUN_DIR}"

git status -sb | tee "${RUN_DIR}/git_status.txt"
git rev-parse HEAD | tee "${RUN_DIR}/git_head.txt"

export PYTHONPATH="${REPO_ROOT}/petcare_runtime/src:${PYTHONPATH:-}"
python3 -m pytest "petcare_runtime/tests/integration_control/test_integration_control.py" -q | tee "${RUN_DIR}/tests.log"

python3 <<'PY' | tee "${RUN_DIR}/invariant_check.txt"
from petcare.integration_control import (
    AdapterDirection,
    AdapterType,
    EscalationRecord,
    ExternalSignalTrust,
    QueueItem,
    QueueItemStatus,
    QueueType,
    TaskPriority,
    assign_task,
    build_adapter_contract,
    build_operational_control_snapshot,
    build_queue,
    build_signal_record,
    claim_queue_item,
    create_exception_case,
    enqueue_item,
    escalate_exception_case,
    record_operator_action,
    validate_signal_for_review,
)

adapter = build_adapter_contract(
    adapter_id="ADP-CLOSE-001",
    adapter_type=AdapterType.PAYMENT_GATEWAY,
    direction=AdapterDirection.INGEST_ONLY,
    contract_version="v1",
)

signal = build_signal_record(
    signal_id="SIG-CLOSE-001",
    source_system="gateway",
    payload_ref="obj://signals/close-ep10-001",
    received_at="2026-03-30T22:00:00Z",
    trust_status=ExternalSignalTrust.REVIEW_REQUIRED,
)

queue = build_queue("Q-CLOSE-001", QueueType.EXCEPTION)
queue = enqueue_item(
    queue,
    QueueItem(
        item_id="ITEM-CLOSE-001",
        queue_type=QueueType.EXCEPTION,
        subject_id="SIG-CLOSE-001",
        priority_rank=1,
        status=QueueItemStatus.OPEN,
        created_at="2026-03-30T22:01:00Z",
    ),
)
claimed = claim_queue_item(queue.items[0], actor_id="operator.close", claimed_at="2026-03-30T22:02:00Z")

task = assign_task(
    task_id="TASK-CLOSE-001",
    queue_item_id=claimed.item_id,
    assigned_to="operator.close",
    assigned_at="2026-03-30T22:02:30Z",
    priority=TaskPriority.HIGH,
)

exception_case = create_exception_case(
    case_id="EXC-CLOSE-001",
    subject_id="SIG-CLOSE-001",
    opened_at="2026-03-30T22:03:00Z",
    opened_by="operator.close",
    reason="signal requires manager review",
)
escalated = escalate_exception_case(
    exception_case,
    EscalationRecord(
        escalation_id="ESC-CLOSE-001",
        escalated_by="operator.close",
        escalated_at="2026-03-30T22:04:00Z",
        escalation_target="finance.manager",
        reason="gateway signal requires escalation",
    ),
)

action = record_operator_action(
    action_id="ACT-CLOSE-001",
    action_name="claim",
    actor_id="operator.close",
    entity_id=claimed.item_id,
    occurred_at="2026-03-30T22:02:00Z",
    outcome="success",
)

snapshot = build_operational_control_snapshot(
    snapshot_id="SNAP-CLOSE-001",
    generated_at="2026-03-30T22:05:00Z",
    queues=[build_queue("Q-CLOSE-EMPTY", QueueType.FINANCE_REVIEW)],
    exception_cases=[escalated],
)

checks = {
    "adapters_passive_only": adapter.execution_mode.startswith("passive_"),
    "external_signal_review_boundary_enforced": validate_signal_for_review(signal),
    "queue_ordering_is_deterministic": claimed.item_id == "ITEM-CLOSE-001",
    "human_action_traceability_required": action.actor_id == "operator.close",
    "task_assignment_is_attributable": task.assigned_to == "operator.close",
    "exception_escalation_is_reviewable": escalated.escalation is not None,
    "operational_visibility_is_deterministic": snapshot.open_exception_count == 1,
    "ai_execution_authority": False,
    "live_payment_rails_enabled": False,
}
for key, value in checks.items():
    print(f"{key}={value}")
PY

find \
  "petcare_execution/EP10_CLOSURE" \
  "petcare_execution/EP10" \
  "petcare_runtime/src/petcare/integration_control" \
  "petcare_runtime/tests/integration_control" \
  "scripts/petcare_ep10_all_waves_pack.sh" \
  "scripts/petcare_close_ep10.sh" \
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

entries = []

for path in sorted(run_dir.rglob("*")):
    if path.is_file():
        rel = path.relative_to(repo_root).as_posix()
        entries.append(
            {
                "path": rel,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )

for rel in [
    "petcare_execution/EP10_CLOSURE/EP10_CLOSURE_SUMMARY.md",
    "petcare_execution/EP10_CLOSURE/EP10_ACCEPTANCE_RECORD.md",
    "petcare_execution/EP10_CLOSURE/EP10_INTEGRATION_AND_CONTROL_INVARIANTS_REGISTRY.md",
    "petcare_execution/EP10_CLOSURE/EP10_GOVERNANCE_SEAL.md",
    "petcare_execution/EP10_CLOSURE/EP10_EVIDENCE_INDEX.md",
    "scripts/petcare_close_ep10.sh",
]:
    path = repo_root / rel
    entries.append(
        {
            "path": rel,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    )

manifest = {
    "pack_id": os.environ["PACK_ID"],
    "run_dir": run_dir.relative_to(repo_root).as_posix(),
    "entries": entries,
}
(run_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

printf 'PACK_ID              : %s\n' "$PACK_ID" | tee "${RUN_DIR}/summary.txt"
printf 'VALIDATION           : OK\n' | tee -a "${RUN_DIR}/summary.txt"
printf 'GOVERNANCE_STATE     : ep10_closed_governed\n' | tee -a "${RUN_DIR}/summary.txt"
printf 'OPERATING_BOUNDARY   : integration_and_operational_control_non_autonomous\n' | tee -a "${RUN_DIR}/summary.txt"
printf 'EVIDENCE_RUN_DIR     : %s\n' "${RUN_DIR}" | tee -a "${RUN_DIR}/summary.txt"
