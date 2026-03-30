from petcare.partner_network.execution_visibility import (
    EXECUTION_EVENT_ACCEPTED,
    EXECUTION_EVENT_COMPLETED,
    EXECUTION_EVENT_IN_PROGRESS,
    ExecutionEventInput,
)
from petcare.partner_network.execution_visibility_repository import ExecutionVisibilityRepository
from petcare.partner_network.execution_visibility_service import ExecutionVisibilityService
from petcare.partner_network.orders import StructuredOrderInput
from petcare.partner_network.orders_repository import OrdersRepository
from petcare.partner_network.orders_service import OrdersService
from petcare.partner_network.pricing import PricingRule
from petcare.partner_network.pricing_repository import PricingRepository
from petcare.partner_network.settlement_export import SettlementExportInput
from petcare.partner_network.settlement_export_query import SettlementExportQuery
from petcare.partner_network.settlement_export_repository import SettlementExportRepository
from petcare.partner_network.settlement_export_service import SettlementExportService
from petcare.partner_network.settlement_preparation import SettlementPreparationInput
from petcare.partner_network.settlement_preparation_repository import SettlementPreparationRepository
from petcare.partner_network.settlement_preparation_service import SettlementPreparationService
from petcare.partner_network.settlement_review import REVIEW_DECISION_APPROVE, REVIEW_DECISION_REJECT, SettlementReviewDecisionInput
from petcare.partner_network.settlement_review_repository import SettlementReviewRepository
from petcare.partner_network.settlement_review_service import SettlementReviewService


def build_services():
    pricing_repository = PricingRepository()
    orders_repository = OrdersRepository()
    execution_visibility_repository = ExecutionVisibilityRepository()
    settlement_preparation_repository = SettlementPreparationRepository()
    settlement_review_repository = SettlementReviewRepository()
    settlement_export_repository = SettlementExportRepository()

    orders_service = OrdersService(orders_repository, pricing_repository)
    execution_visibility_service = ExecutionVisibilityService(execution_visibility_repository, orders_repository)
    settlement_preparation_service = SettlementPreparationService(settlement_preparation_repository, orders_repository, execution_visibility_repository)
    settlement_review_service = SettlementReviewService(settlement_review_repository, settlement_preparation_repository)
    settlement_export_service = SettlementExportService(settlement_export_repository, settlement_review_repository)
    return (
        pricing_repository,
        settlement_review_repository,
        settlement_export_repository,
        orders_service,
        execution_visibility_service,
        settlement_preparation_service,
        settlement_review_service,
        settlement_export_service,
    )


def seed_approved_review(pricing_repository, orders_service, execution_visibility_service, settlement_preparation_service, settlement_review_service, order_id, settlement_preparation_id, review_id):
    pricing_repository.save_rule(PricingRule(rule_id=f"rule-{order_id}", partner_id="partner-001", catalog_item_id="catalog-001", base_price=100.0, margin_percentage=10.0, promo_percentage=5.0, min_quantity=1, max_quantity=10, active=True, ai_execution_authority=False))
    orders_service.create_order(StructuredOrderInput(order_id=order_id, partner_id="partner-001", catalog_item_id="catalog-001", quantity=2, requested_by="ops.user", pricing_rule_id=f"rule-{order_id}", quoted_final_price=209.0, currency="SAR"))
    orders_service.validate_order(order_id)
    orders_service.route_order(order_id)
    execution_visibility_service.record_event(ExecutionEventInput(order_id=order_id, event_type=EXECUTION_EVENT_ACCEPTED, recorded_by="partner.ops", partner_id="partner-001"))
    execution_visibility_service.record_event(ExecutionEventInput(order_id=order_id, event_type=EXECUTION_EVENT_IN_PROGRESS, recorded_by="partner.ops", partner_id="partner-001"))
    execution_visibility_service.record_event(ExecutionEventInput(order_id=order_id, event_type=EXECUTION_EVENT_COMPLETED, recorded_by="partner.ops", partner_id="partner-001"))
    settlement_preparation_service.prepare_record(SettlementPreparationInput(settlement_preparation_id=settlement_preparation_id, order_id=order_id, prepared_by="finance.ops"))
    settlement_review_service.enqueue_review_item(review_id, settlement_preparation_id)
    settlement_review_service.record_decision(SettlementReviewDecisionInput(review_id=review_id, reviewer_id="finance.reviewer", decision=REVIEW_DECISION_APPROVE, reason_code="MATCHED_EXECUTION_EVIDENCE"))


def test_settlement_export_package_created_after_approved_review() -> None:
    (pricing_repository, _, _, orders_service, execution_visibility_service, settlement_preparation_service, settlement_review_service, settlement_export_service) = build_services()
    seed_approved_review(pricing_repository, orders_service, execution_visibility_service, settlement_preparation_service, settlement_review_service, "order-export-001", "settlement-prep-export-001", "review-export-001")

    package = settlement_export_service.create_export_package(SettlementExportInput(export_package_id="export-package-001", review_id="review-export-001", prepared_by="finance.ops", handoff_target="finance_handover_queue"))

    assert package.status == "HANDOFF_READY"
    assert package.export_delivery_executed is False
    assert package.manifest.human_approved is True
    assert package.manifest.handoff_only is True
    assert package.audit_trace["payment_execution_enabled"] is False


def test_settlement_export_requires_approved_review() -> None:
    (_, _, _, _, _, _, _, settlement_export_service) = build_services()

    try:
        settlement_export_service.create_export_package(SettlementExportInput(export_package_id="export-package-002", review_id="missing-review", prepared_by="finance.ops", handoff_target="finance_handover_queue"))
        assert False
    except ValueError as exc:
        assert str(exc) == "review_id not found"


def test_settlement_export_rejects_non_approved_review() -> None:
    (pricing_repository, _, _, orders_service, execution_visibility_service, settlement_preparation_service, settlement_review_service, settlement_export_service) = build_services()

    pricing_repository.save_rule(PricingRule(rule_id="rule-order-export-003", partner_id="partner-001", catalog_item_id="catalog-001", base_price=100.0, active=True, ai_execution_authority=False))
    orders_service.create_order(StructuredOrderInput(order_id="order-export-003", partner_id="partner-001", catalog_item_id="catalog-001", quantity=1, requested_by="ops.user", pricing_rule_id="rule-order-export-003", quoted_final_price=100.0, currency="SAR"))
    orders_service.validate_order("order-export-003")
    orders_service.route_order("order-export-003")
    execution_visibility_service.record_event(ExecutionEventInput(order_id="order-export-003", event_type=EXECUTION_EVENT_ACCEPTED, recorded_by="partner.ops", partner_id="partner-001"))
    execution_visibility_service.record_event(ExecutionEventInput(order_id="order-export-003", event_type=EXECUTION_EVENT_IN_PROGRESS, recorded_by="partner.ops", partner_id="partner-001"))
    execution_visibility_service.record_event(ExecutionEventInput(order_id="order-export-003", event_type=EXECUTION_EVENT_COMPLETED, recorded_by="partner.ops", partner_id="partner-001"))
    settlement_preparation_service.prepare_record(SettlementPreparationInput(settlement_preparation_id="settlement-prep-export-003", order_id="order-export-003", prepared_by="finance.ops"))
    settlement_review_service.enqueue_review_item("review-export-003", "settlement-prep-export-003")
    settlement_review_service.record_decision(SettlementReviewDecisionInput(review_id="review-export-003", reviewer_id="finance.reviewer", decision=REVIEW_DECISION_REJECT, reason_code="MANUAL_EXCEPTION_REQUIRES_REWORK"))

    try:
        settlement_export_service.create_export_package(SettlementExportInput(export_package_id="export-package-003", review_id="review-export-003", prepared_by="finance.ops", handoff_target="finance_handover_queue"))
        assert False
    except ValueError as exc:
        assert str(exc) == "review must be APPROVED before export package creation"


def test_settlement_export_rejects_duplicate_review_package() -> None:
    (pricing_repository, _, _, orders_service, execution_visibility_service, settlement_preparation_service, settlement_review_service, settlement_export_service) = build_services()
    seed_approved_review(pricing_repository, orders_service, execution_visibility_service, settlement_preparation_service, settlement_review_service, "order-export-004", "settlement-prep-export-004", "review-export-004")
    settlement_export_service.create_export_package(SettlementExportInput(export_package_id="export-package-004a", review_id="review-export-004", prepared_by="finance.ops", handoff_target="finance_handover_queue"))

    try:
        settlement_export_service.create_export_package(SettlementExportInput(export_package_id="export-package-004b", review_id="review-export-004", prepared_by="finance.ops", handoff_target="finance_handover_queue"))
        assert False
    except ValueError as exc:
        assert str(exc) == "review_id already has an export package"


def test_settlement_export_query_and_summary() -> None:
    (pricing_repository, _, settlement_export_repository, orders_service, execution_visibility_service, settlement_preparation_service, settlement_review_service, settlement_export_service) = build_services()
    query = SettlementExportQuery()

    for order_id, prep_id, review_id, pkg_id in [
        ("order-export-005", "settlement-prep-export-005", "review-export-005", "export-package-005"),
        ("order-export-006", "settlement-prep-export-006", "review-export-006", "export-package-006"),
    ]:
        seed_approved_review(pricing_repository, orders_service, execution_visibility_service, settlement_preparation_service, settlement_review_service, order_id, prep_id, review_id)
        settlement_export_service.create_export_package(SettlementExportInput(export_package_id=pkg_id, review_id=review_id, prepared_by="finance.ops", handoff_target="finance_handover_queue"))

    packages = settlement_export_repository.list_for_partner("partner-001")
    handoff_ready = query.list_handoff_ready(packages)
    summary = settlement_export_service.summarize_partner_exports("partner-001")

    assert len(handoff_ready) == 2
    assert handoff_ready[0].status == "HANDOFF_READY"
    assert summary.total_packages == 2
    assert summary.handoff_ready_count == 2
