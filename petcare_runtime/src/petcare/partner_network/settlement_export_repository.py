from typing import Dict, List, Optional

from .settlement_export import SettlementExportPackage


class SettlementExportRepository:
    def __init__(self) -> None:
        self._packages: Dict[str, SettlementExportPackage] = {}

    def save(self, package: SettlementExportPackage) -> SettlementExportPackage:
        package.validate()
        self._packages[package.export_package_id] = package
        return package

    def get(self, export_package_id: str) -> Optional[SettlementExportPackage]:
        return self._packages.get(export_package_id)

    def get_by_review_id(self, review_id: str) -> Optional[SettlementExportPackage]:
        matches = [package for package in self._packages.values() if package.review_id == review_id]
        matches.sort(key=lambda item: item.export_package_id)
        return matches[0] if matches else None

    def list_for_partner(self, partner_id: str) -> List[SettlementExportPackage]:
        return sorted(
            [package for package in self._packages.values() if package.partner_id == partner_id],
            key=lambda item: item.export_package_id,
        )
