from __future__ import annotations

from decimal import Decimal

from petcare.payment_activation import (
    ExecutionClass,
    FinalizationStatus,
    RailType,
    add_second_authorization,
    attach_dispatch,
    attach_finalization,
    attach_treasury_check,
    authorization_event_name,
    authorize_execution,
    build_audit_event,
    build_rail_connector_contract,
    cancel_execution,
    create_controlled_execution_case,
    dispatch_event_name,
    dispatch_execution,
    fail_execution,
    finalization_event_name,
    finalize_settlement,
    pause_execution,
    retry_execution,
    run_treasury_check,
    safeguard_event_name,
)


def test_execution_authorization_and_dual_control() -> None:
    auth = authorize_execution(
        authorization_id="AUTH-001",
        execution_id="EXEC-001",
        execution_class=ExecutionClass.HIGH_VALUE,
        approved_by="finance.manager",
        approved_at="2026-03-30T23:00:00Z",
        reason="approved scheduled payout",
    )
    dual = add_second_authorization(
        auth,
        second_approved_by="finance.director",
        second_approved_at="2026-03-30T23:01:00Z",
    )

    assert auth.status.value == "authorized"
    assert dual.status.value == "dual_authorized"
    assert dual.second_approved_by == "finance.director"


def test_treasury_sufficiency_blocks_or_allows_dispatch() -> None:
    auth = authorize_execution(
        authorization_id="AUTH-002",
        execution_id="EXEC-002",
        execution_class=ExecutionClass.STANDARD,
        approved_by="finance.manager",
        approved_at="2026-03-30T23:02:00Z",
        reason="approved standard payout",
    )
    connector = build_rail_connector_contract(
        connector_id="RAIL-001",
        rail_type=RailType.GATEWAY_API,
        contract_version="v1",
    )

    blocked_check = run_treasury_check(
        check_id="CHK-001",
        execution_id="EXEC-002",
        available_balance=Decimal("50.00"),
        required_amount=Decimal("100.00"),
        checked_at="2026-03-30T23:03:00Z",
        checked_by="treasury.operator",
    )
    blocked_dispatch = dispatch_execution(
        dispatch_id="DSP-001",
        execution_id="EXEC-002",
        connector=connector,
        authorization=auth,
        treasury_check=blocked_check,
        dispatched_at="2026-03-30T23:04:00Z",
        dispatched_by="finance.operator",
    )

    allowed_check = run_treasury_check(
        check_id="CHK-002",
        execution_id="EXEC-002",
        available_balance=Decimal("150.00"),
        required_amount=Decimal("100.00"),
        checked_at="2026-03-30T23:05:00Z",
        checked_by="treasury.operator",
    )
    allowed_dispatch = dispatch_execution(
        dispatch_id="DSP-002",
        execution_id="EXEC-002",
        connector=connector,
        authorization=auth,
        treasury_check=allowed_check,
        dispatched_at="2026-03-30T23:06:00Z",
        dispatched_by="finance.operator",
    )

    assert blocked_check.status.value == "insufficient"
    assert blocked_dispatch.status.value == "dispatch_blocked"
    assert allowed_check.status.value == "sufficient"
    assert allowed_dispatch.status.value == "dispatched"


def test_execution_safeguards_are_explicit() -> None:
    paused_state, pause_record = pause_execution(
        execution_id="EXEC-003",
        paused_at="2026-03-30T23:07:00Z",
        paused_by="finance.manager",
        reason="manual pause for review",
    )
    retry_state, retry_record = retry_execution(
        execution_id="EXEC-003",
        retried_at="2026-03-30T23:08:00Z",
        retried_by="finance.operator",
        reason="connector recovered",
    )
    failed_state, failure_record = fail_execution(
        execution_id="EXEC-003",
        failed_at="2026-03-30T23:09:00Z",
        failure_code="RAIL_TIMEOUT",
        reason="rail timed out",
    )
    cancelled_state = cancel_execution("EXEC-003")

    assert paused_state.value == "paused"
    assert retry_state.value == "retrying"
    assert failed_state.value == "failed"
    assert cancelled_state.value == "cancelled"
    assert pause_record.reason == "manual pause for review"
    assert retry_record.reason == "connector recovered"
    assert failure_record.failure_code == "RAIL_TIMEOUT"


def test_settlement_finalization_requires_dispatch_outcome() -> None:
    auth = authorize_execution(
        authorization_id="AUTH-004",
        execution_id="EXEC-004",
        execution_class=ExecutionClass.STANDARD,
        approved_by="finance.manager",
        approved_at="2026-03-30T23:10:00Z",
        reason="approved finalization test",
    )
    treasury = run_treasury_check(
        check_id="CHK-004",
        execution_id="EXEC-004",
        available_balance=Decimal("200.00"),
        required_amount=Decimal("100.00"),
        checked_at="2026-03-30T23:11:00Z",
        checked_by="treasury.operator",
    )
    connector = build_rail_connector_contract(
        connector_id="RAIL-004",
        rail_type=RailType.BANK_API,
        contract_version="v1",
    )
    dispatch = dispatch_execution(
        dispatch_id="DSP-004",
        execution_id="EXEC-004",
        connector=connector,
        authorization=auth,
        treasury_check=treasury,
        dispatched_at="2026-03-30T23:12:00Z",
        dispatched_by="finance.operator",
    )
    finalization = finalize_settlement(
        finalization_id="FIN-001",
        execution_id="EXEC-004",
        dispatch=dispatch,
        finalized_at="2026-03-30T23:13:00Z",
        finalized_by="finance.manager",
    )

    assert dispatch.status.value == "dispatched"
    assert finalization.status == FinalizationStatus.FINALIZED
    assert finalization.reconciliation_required is True
    assert finalization.ledger_link_required is True


def test_controlled_execution_workflow_is_attachable_and_traceable() -> None:
    auth = authorize_execution(
        authorization_id="AUTH-005",
        execution_id="EXEC-005",
        execution_class=ExecutionClass.STANDARD,
        approved_by="finance.manager",
        approved_at="2026-03-30T23:14:00Z",
        reason="workflow assembly",
    )
    case = create_controlled_execution_case("EXEC-005", auth)
    treasury = run_treasury_check(
        check_id="CHK-005",
        execution_id="EXEC-005",
        available_balance=Decimal("120.00"),
        required_amount=Decimal("100.00"),
        checked_at="2026-03-30T23:15:00Z",
        checked_by="treasury.operator",
    )
    connector = build_rail_connector_contract(
        connector_id="RAIL-005",
        rail_type=RailType.PAYOUT_PROVIDER,
        contract_version="v1",
    )
    dispatch = dispatch_execution(
        dispatch_id="DSP-005",
        execution_id="EXEC-005",
        connector=connector,
        authorization=auth,
        treasury_check=treasury,
        dispatched_at="2026-03-30T23:16:00Z",
        dispatched_by="finance.operator",
    )
    finalization = finalize_settlement(
        finalization_id="FIN-005",
        execution_id="EXEC-005",
        dispatch=dispatch,
        finalized_at="2026-03-30T23:17:00Z",
        finalized_by="finance.manager",
    )

    case = attach_treasury_check(case, treasury)
    case = attach_dispatch(case, dispatch)
    case = attach_finalization(case, finalization)

    assert case.treasury_check is not None
    assert case.dispatch is not None
    assert case.finalization is not None


def test_ep11_audit_events_are_scoped() -> None:
    auth_event = build_audit_event(
        event_id="AUD-001",
        event_name=authorization_event_name("authorized"),
        entity_id="AUTH-001",
        occurred_at="2026-03-30T23:18:00Z",
        actor_id="finance.manager",
    )
    dispatch_event = build_audit_event(
        event_id="AUD-002",
        event_name=dispatch_event_name("dispatched"),
        entity_id="DSP-001",
        occurred_at="2026-03-30T23:19:00Z",
        actor_id="finance.operator",
    )
    safeguard_event = build_audit_event(
        event_id="AUD-003",
        event_name=safeguard_event_name("paused"),
        entity_id="EXEC-003",
        occurred_at="2026-03-30T23:20:00Z",
        actor_id="finance.manager",
    )
    final_event = build_audit_event(
        event_id="AUD-004",
        event_name=finalization_event_name("finalized"),
        entity_id="FIN-001",
        occurred_at="2026-03-30T23:21:00Z",
        actor_id="finance.manager",
    )

    assert auth_event.event_name == "payment_activation.authorization.authorized"
    assert dispatch_event.event_name == "payment_activation.dispatch.dispatched"
    assert safeguard_event.event_name == "payment_activation.safeguard.paused"
    assert final_event.event_name == "payment_activation.finalization.finalized"
