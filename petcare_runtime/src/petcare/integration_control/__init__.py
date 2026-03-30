"""Integration and operational control domain for PetCare EP-10."""

from .actions import (
    assign_task,
    claim_queue_item,
    release_queue_item,
    record_operator_action,
)
from .adapters import (
    AdapterContract,
    AdapterDirection,
    AdapterType,
    ExternalReferenceMap,
    build_adapter_contract,
    build_external_reference_map,
)
from .audit import (
    AuditEvent,
    build_audit_event,
    adapter_transition_event_name,
    queue_transition_event_name,
    human_action_event_name,
)
from .exceptions import (
    EscalationRecord,
    ExceptionCase,
    ExceptionStatus,
    create_exception_case,
    escalate_exception_case,
    resolve_exception_case,
)
from .queues import (
    OperationalQueue,
    QueueItem,
    QueueItemStatus,
    QueueType,
    build_queue,
    enqueue_item,
    reorder_queue,
)
from .signals import (
    ExternalSignalRecord,
    ExternalSignalTrust,
    build_signal_record,
    validate_signal_for_review,
)
from .tasks import (
    OperatorTask,
    TaskAssignmentStatus,
    TaskPriority,
)
from .visibility import (
    OperationalControlSnapshot,
    build_operational_control_snapshot,
)

__all__ = [
    "AdapterContract",
    "AdapterDirection",
    "AdapterType",
    "AuditEvent",
    "EscalationRecord",
    "ExceptionCase",
    "ExceptionStatus",
    "ExternalReferenceMap",
    "ExternalSignalRecord",
    "ExternalSignalTrust",
    "OperationalControlSnapshot",
    "OperationalQueue",
    "OperatorTask",
    "QueueItem",
    "QueueItemStatus",
    "QueueType",
    "TaskAssignmentStatus",
    "TaskPriority",
    "adapter_transition_event_name",
    "assign_task",
    "build_adapter_contract",
    "build_audit_event",
    "build_external_reference_map",
    "build_operational_control_snapshot",
    "build_queue",
    "build_signal_record",
    "claim_queue_item",
    "create_exception_case",
    "enqueue_item",
    "escalate_exception_case",
    "human_action_event_name",
    "queue_transition_event_name",
    "record_operator_action",
    "release_queue_item",
    "reorder_queue",
    "resolve_exception_case",
    "validate_signal_for_review",
]
