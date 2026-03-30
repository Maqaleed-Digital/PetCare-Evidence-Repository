from .settlement_export import (
    DECISION_CLASSIFICATION_NON_AUTONOMOUS,
    SETTLEMENT_EXPORT_STATUS_HANDOFF_READY,
    SettlementExportInput,
    SettlementExportManifest,
    SettlementExportPackage,
    SettlementExportSummary,
)
from .settlement_export_repository import SettlementExportRepository
from .settlement_review import REVIEW_DECISION_APPROVE, SETTLEMENT_REVIEW_STATUS_APPROVED
from .settlement_review_repository import SettlementReviewRepository


class SettlementExportService:
    def __init__(
        self,
        settlement_export_repository: SettlementExportRepository,
        settlement_review_repository: SettlementReviewRepository,
    ) -> None:
        self._settlement_export_repository = settlement_export_repository
        self._settlement_review_repository = settlement_review_repository

    def create_export_package(self, export_input: SettlementExportInput) -> SettlementExportPackage:
        export_input.validate()

        if self._settlement_export_repository.get(export_input.export_package_id) is not None:
            raise ValueError("export_package_id already exists")

        if self._settlement_export_repository.get_by_review_id(export_input.review_id) is not None:
            raise ValueError("review_id already has an export package")

        queue_item = self._settlement_review_repository.get_queue_item(export_input.review_id)
        if queue_item is None:
            raise ValueError("review_id not found")

        if queue_item.status != SETTLEMENT_REVIEW_STATUS_APPROVED:
            raise ValueError("review must be APPROVED before export package creation")

        decision_record = self._settlement_review_repository.get_decision_record_by_review_id(export_input.review_id)
        if decision_record is None:
            raise ValueError("approved review decision record not found")

        if decision_record.decision != REVIEW_DECISION_APPROVE:
            raise ValueError("review decision must be APPROVE before export package creation")

        manifest = SettlementExportManifest(
            manifest_id=f"{export_input.export_package_id}-manifest",
            export_package_id=export_input.export_package_id,
            review_id=export_input.review_id,
            settlement_preparation_id=queue_item.settlement_preparation_id,
            order_id=queue_item.order_id,
            partner_id=queue_item.partner_id,
            quoted_final_price=queue_item.quoted_final_price,
            currency=queue_item.currency,
            manifest_version="1.0",
            immutable_fields={
                "review_id": export_input.review_id,
                "settlement_preparation_id": queue_item.settlement_preparation_id,
                "order_id": queue_item.order_id,
                "partner_id": queue_item.partner_id,
                "quoted_final_price": queue_item.quoted_final_price,
                "currency": queue_item.currency,
                "review_status": queue_item.status,
                "review_decision": decision_record.decision,
                "reason_code": decision_record.reason_code,
            },
            human_approved=True,
            handoff_only=True,
            decision_classification=DECISION_CLASSIFICATION_NON_AUTONOMOUS,
            ai_execution_authority=False,
        )

        package = SettlementExportPackage(
            export_package_id=export_input.export_package_id,
            review_id=export_input.review_id,
            settlement_preparation_id=queue_item.settlement_preparation_id,
            order_id=queue_item.order_id,
            partner_id=queue_item.partner_id,
            status=SETTLEMENT_EXPORT_STATUS_HANDOFF_READY,
            handoff_target=export_input.handoff_target,
            export_delivery_executed=False,
            manifest=manifest,
            audit_trace={
                "prepared_by": export_input.prepared_by,
                "notes": export_input.notes,
                "handoff_target": export_input.handoff_target,
                "human_approved": True,
                "handoff_only": True,
                "payment_execution_enabled": False,
                "settlement_execution_enabled": False,
                "payout_execution_enabled": False,
                "reconciliation_execution_enabled": False,
                "posting_execution_enabled": False,
                "export_delivery_executed": False,
            },
            decision_classification=DECISION_CLASSIFICATION_NON_AUTONOMOUS,
            ai_execution_authority=False,
        )
        return self._settlement_export_repository.save(package)

    def summarize_partner_exports(self, partner_id: str) -> SettlementExportSummary:
        packages = self._settlement_export_repository.list_for_partner(partner_id)
        if not packages:
            raise ValueError("no settlement export packages found for partner")

        handoff_ready_count = len(
            [package for package in packages if package.status == SETTLEMENT_EXPORT_STATUS_HANDOFF_READY]
        )

        summary = SettlementExportSummary(
            partner_id=partner_id,
            total_packages=len(packages),
            handoff_ready_count=handoff_ready_count,
            decision_classification=DECISION_CLASSIFICATION_NON_AUTONOMOUS,
            ai_execution_authority=False,
            packages=packages,
        )
        summary.validate()
        return summary
