from typing import List

from .settlement_export import SETTLEMENT_EXPORT_STATUS_HANDOFF_READY, SettlementExportPackage


class SettlementExportQuery:
    def list_handoff_ready(self, packages: List[SettlementExportPackage]) -> List[SettlementExportPackage]:
        return sorted(
            [package for package in packages if package.status == SETTLEMENT_EXPORT_STATUS_HANDOFF_READY],
            key=lambda item: item.export_package_id,
        )
