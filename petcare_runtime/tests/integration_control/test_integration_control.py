from __future__ import annotations

from petcare.integration_control import (
    AdapterDirection,
    AdapterType,
    EscalationRecord,
    ExternalSignalTrust,
    QueueItem,
    QueueItemStatus,
    QueueType,
    TaskPriority,
    adapter_transition_event_name,
    assign_task,
    build_adapter_contract,
    build_audit_event,
    build_external_reference_map,
    build_operational_control_snapshot,
    build_queue,
    build_signal_record,
    claim_queue_item,
    create_exception_case,
    enqueue_item,
    escalate_exception_case,
    human_action_event_name,
    queue_transition_event_name,
    record_operator_action,
    release_queue_item,
    reorder_queue,
    resolve_exception_case,
    validate_signal_for_review,
)


def test_adapter_contracts_remain_passive_and_reference_mapping_is_traceable() -> None:
    adapter = build_adapter_contract(
        adapter_id="ADP-001",
        adapter_type=AdapterType.ERP,
        direction=AdapterDirection.EXPORT_ONLY,
        contract_version="v1",
    )
    mapping = build_external_reference_map(
        mapping_id="MAP-001",
        internal_entity_id="INS-001",
        external_system="erp",
        external_reference_id="ERP-REF-001",
        created_at="2026-03-30T21:00:00Z",
    )

    assert adapter.execution_mode == "passive_export_only"
    assert mapping.external_reference_id == "ERP-REF-001"


def test_external_signals_are_classified_and_review_flagged() -> None:
    signal = build_signal_record(
        signal_id="SIG-001",
        source_system="gateway",
        payload_ref="obj://signals/001",
        received_at="2026-03-30T21:01:00Z",
        trust_status=ExternalSignalTrust.REVIEW_REQUIRED,
    )

    assert signal.trust_status == ExternalSignalTrust.REVIEW_REQUIRED
    assert validate_signal_for_review(signal) is True


def test_operational_queue_ordering_is_deterministic() -> None:
    queue = build_queue("Q-001", QueueType.FINANCE_REVIEW)
    queue = enqueue_item(
        queue,
        QueueItem(
            item_id="ITEM-002",
            queue_type=QueueType.FINANCE_REVIEW,
            subject_id="INV-002",
            priority_rank=2,
            status=QueueItemStatus.OPEN,
            created_at="2026-03-30T21:03:00Z",
        ),
    )
    queue = enqueue_item(
        queue,
        QueueItem(
            item_id="ITEM-001",
            queue_type=QueueType.FINANCE_REVIEW,
            subject_id="INV-001",
            priority_rank=1,
            status=QueueItemStatus.OPEN,
            created_at="2026-03-30T21:02:00Z",
        ),
    )
    queue = reorder_queue(queue)

    assert [item.item_id for item in queue.items] == ["ITEM-001", "ITEM-002"]


def test_human_action_claim_release_and_task_assignment_are_attributable() -> None:
    item = QueueItem(
        item_id="ITEM-001",
        queue_type=QueueType.APPROVAL,
        subject_id="SET-001",
        priority_rank=1,
        status=QueueItemStatus.OPEN,
        created_at="2026-03-30T21:04:00Z",
    )
    claimed = claim_queue_item(item, actor_id="operator.a", claimed_at="2026-03-30T21:05:00Z")
    task = assign_task(
        task_id="TASK-001",
        queue_item_id=claimed.item_id,
        assigned_to="operator.a",
        assigned_at="2026-03-30T21:05:30Z",
        priority=TaskPriority.HIGH,
    )
    action = record_operator_action(
        action_id="ACT-001",
        action_name="claim",
        actor_id="operator.a",
        entity_id=claimed.item_id,
        occurred_at="2026-03-30T21:05:00Z",
        outcome="success",
    )
    released = release_queue_item(claimed)

    assert claimed.claimed_by == "operator.a"
    assert task.assigned_to == "operator.a"
    assert action.actor_id == "operator.a"
    assert released.status == QueueItemStatus.RELEASED


def test_exception_and_escalation_workflow_is_reviewable() -> None:
    case = create_exception_case(
        case_id="EXC-001",
        subject_id="SIG-001",
        opened_at="2026-03-30T21:06:00Z",
        opened_by="system.monitor",
        reason="signal trust review required",
    )
    escalated = escalate_exception_case(
        case,
        EscalationRecord(
            escalation_id="ESC-001",
            escalated_by="operator.a",
            escalated_at="2026-03-30T21:07:00Z",
            escalation_target="finance.manager",
            reason="financial signal requires manager review",
        ),
    )
    resolved = resolve_exception_case(
        escalated,
        resolved_at="2026-03-30T21:08:00Z",
        resolved_by="finance.manager",
    )

    assert escalated.status.value == "escalated"
    assert resolved.status.value == "resolved"
    assert resolved.resolved_by == "finance.manager"


def test_operational_visibility_and_audit_events_are_scoped() -> None:
    queue = build_queue("Q-001", QueueType.EXCEPTION)
    queue = enqueue_item(
        queue,
        QueueItem(
            item_id="ITEM-003",
            queue_type=QueueType.EXCEPTION,
            subject_id="EXC-001",
            priority_rank=1,
            status=QueueItemStatus.OPEN,
            created_at="2026-03-30T21:09:00Z",
        ),
    )
    exception_case = create_exception_case(
        case_id="EXC-002",
        subject_id="INV-002",
        opened_at="2026-03-30T21:10:00Z",
        opened_by="operator.b",
        reason="manual exception review",
    )
    snapshot = build_operational_control_snapshot(
        snapshot_id="SNAP-001",
        generated_at="2026-03-30T21:11:00Z",
        queues=[queue],
        exception_cases=[exception_case],
    )

    adapter_event = build_audit_event(
        event_id="AUD-001",
        event_name=adapter_transition_event_name("exported"),
        entity_id="ADP-001",
        occurred_at="2026-03-30T21:12:00Z",
        actor_id="operator.a",
    )
    queue_event = build_audit_event(
        event_id="AUD-002",
        event_name=queue_transition_event_name("claimed"),
        entity_id="ITEM-003",
        occurred_at="2026-03-30T21:13:00Z",
        actor_id="operator.a",
    )
    action_event = build_audit_event(
        event_id="AUD-003",
        event_name=human_action_event_name("assign"),
        entity_id="TASK-001",
        occurred_at="2026-03-30T21:14:00Z",
        actor_id="operator.a",
    )

    assert snapshot.open_queue_item_count == 1
    assert snapshot.open_exception_count == 1
    assert adapter_event.event_name == "integration_control.adapter.exported"
    assert queue_event.event_name == "integration_control.queue.claimed"
    assert action_event.event_name == "integration_control.action.assign"
