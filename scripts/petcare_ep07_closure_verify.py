from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_FILES = [
    "petcare_execution/ep07_closure/EP07_CLOSURE_SUMMARY.md",
    "petcare_execution/ep07_closure/EP07_GOVERNANCE_SEAL.json",
    "petcare_execution/ep07_closure/EP07_WAVE_REGISTRY.json",
    "petcare_execution/ep07_closure/EP07_FILE_INVENTORY.txt",
    "petcare_runtime/src/petcare/partner_network/models.py",
    "petcare_runtime/src/petcare/partner_network/repository.py",
    "petcare_runtime/src/petcare/partner_network/service.py",
    "petcare_runtime/src/petcare/partner_network/query.py",
    "petcare_runtime/src/petcare/partner_network/contracts.py",
    "petcare_runtime/src/petcare/partner_network/contracts_repository.py",
    "petcare_runtime/src/petcare/partner_network/contracts_service.py",
    "petcare_runtime/src/petcare/partner_network/contracts_query.py",
    "petcare_runtime/src/petcare/partner_network/catalog.py",
    "petcare_runtime/src/petcare/partner_network/catalog_repository.py",
    "petcare_runtime/src/petcare/partner_network/catalog_service.py",
    "petcare_runtime/src/petcare/partner_network/catalog_query.py",
    "petcare_runtime/src/petcare/partner_network/pricing.py",
    "petcare_runtime/src/petcare/partner_network/pricing_repository.py",
    "petcare_runtime/src/petcare/partner_network/pricing_service.py",
    "petcare_runtime/src/petcare/partner_network/pricing_query.py",
    "petcare_runtime/src/petcare/partner_network/orders.py",
    "petcare_runtime/src/petcare/partner_network/orders_repository.py",
    "petcare_runtime/src/petcare/partner_network/orders_service.py",
    "petcare_runtime/src/petcare/partner_network/orders_query.py",
    "petcare_runtime/src/petcare/partner_network/execution_visibility.py",
    "petcare_runtime/src/petcare/partner_network/execution_visibility_repository.py",
    "petcare_runtime/src/petcare/partner_network/execution_visibility_service.py",
    "petcare_runtime/src/petcare/partner_network/execution_visibility_query.py",
    "petcare_runtime/src/petcare/partner_network/settlement_preparation.py",
    "petcare_runtime/src/petcare/partner_network/settlement_preparation_repository.py",
    "petcare_runtime/src/petcare/partner_network/settlement_preparation_service.py",
    "petcare_runtime/src/petcare/partner_network/settlement_preparation_query.py",
    "petcare_runtime/src/petcare/partner_network/settlement_review.py",
    "petcare_runtime/src/petcare/partner_network/settlement_review_repository.py",
    "petcare_runtime/src/petcare/partner_network/settlement_review_service.py",
    "petcare_runtime/src/petcare/partner_network/settlement_review_query.py",
    "petcare_runtime/src/petcare/partner_network/settlement_export.py",
    "petcare_runtime/src/petcare/partner_network/settlement_export_repository.py",
    "petcare_runtime/src/petcare/partner_network/settlement_export_service.py",
    "petcare_runtime/src/petcare/partner_network/settlement_export_query.py",
    "petcare_runtime/src/petcare/api/routes_ep07_wave01.py",
    "petcare_runtime/src/petcare/api/routes_ep07_wave02.py",
    "petcare_runtime/src/petcare/api/routes_ep07_wave03.py",
    "petcare_runtime/src/petcare/api/routes_ep07_wave04.py",
    "petcare_runtime/src/petcare/api/routes_ep07_wave05.py",
    "petcare_runtime/src/petcare/api/routes_ep07_wave06.py",
    "petcare_runtime/src/petcare/api/routes_ep07_wave07.py",
    "petcare_runtime/src/petcare/api/routes_ep07_wave08.py",
    "petcare_runtime/src/petcare/api/routes_ep07_wave09.py",
    "petcare_runtime/migrations/0019_ep07_wave_01_partner_registry.sql",
    "petcare_runtime/migrations/0020_ep07_wave_02_contract_sla.sql",
    "petcare_runtime/migrations/0021_ep07_wave_03_catalog_ingestion.sql",
    "petcare_runtime/migrations/0022_ep07_wave04_pricing.sql",
    "petcare_runtime/migrations/0023_ep07_wave05_orders.sql",
    "petcare_runtime/migrations/0024_ep07_wave06_execution_visibility.sql",
    "petcare_runtime/migrations/0025_ep07_wave07_settlement_preparation.sql",
    "petcare_runtime/migrations/0026_ep07_wave08_settlement_review.sql",
    "petcare_runtime/migrations/0027_ep07_wave09_settlement_export.sql",
    "petcare_runtime/tests/test_partner_onboarding_registry.py",
    "petcare_runtime/tests/test_partner_contract_sla_governance.py",
    "petcare_runtime/tests/test_partner_catalog_ingestion.py",
    "petcare_runtime/tests/test_partner_pricing_engine.py",
    "petcare_runtime/tests/test_partner_order_structuring.py",
    "petcare_runtime/tests/test_partner_order_execution_visibility.py",
    "petcare_runtime/tests/test_partner_settlement_preparation.py",
    "petcare_runtime/tests/test_partner_settlement_review.py",
    "petcare_runtime/tests/test_partner_settlement_export.py",
]

EXPECTED_WAVES = [
    "WAVE-01",
    "WAVE-02",
    "WAVE-03",
    "WAVE-04",
    "WAVE-05",
    "WAVE-06",
    "WAVE-07",
    "WAVE-08",
    "WAVE-09",
]


def verify_ep07_closure() -> dict:
    missing_files = [path for path in EXPECTED_FILES if not (ROOT / path).exists()]
    if missing_files:
        raise AssertionError(f"Missing expected files: {missing_files}")

    governance_seal_path = ROOT / "petcare_execution/ep07_closure/EP07_GOVERNANCE_SEAL.json"
    wave_registry_path = ROOT / "petcare_execution/ep07_closure/EP07_WAVE_REGISTRY.json"
    inventory_path = ROOT / "petcare_execution/ep07_closure/EP07_FILE_INVENTORY.txt"

    governance_seal = json.loads(governance_seal_path.read_text())
    wave_registry = json.loads(wave_registry_path.read_text())
    inventory_lines = [
        line.strip()
        for line in inventory_path.read_text().splitlines()
        if line.strip()
    ]

    assert governance_seal["status"] == "CLOSED"
    assert governance_seal["governance_seal"] == "ACTIVE"
    assert governance_seal["assertions"]["payment_execution_enabled"] is False
    assert governance_seal["assertions"]["settlement_execution_enabled"] is False
    assert governance_seal["assertions"]["ai_execution_authority"] is False
    assert governance_seal["assertions"]["decision_classification"] == "NON_AUTONOMOUS_DECISION"

    waves = wave_registry["waves"]
    assert len(waves) == 9
    assert [wave["wave"] for wave in waves] == EXPECTED_WAVES
    assert all(wave["status"] == "COMPLETE" for wave in waves)

    missing_inventory_entries = [path for path in EXPECTED_FILES[4:] if path not in inventory_lines]
    if missing_inventory_entries:
        raise AssertionError(f"Missing inventory entries: {missing_inventory_entries}")

    return {
        "pack_id": governance_seal["pack_id"],
        "status": governance_seal["status"],
        "governance_seal": governance_seal["governance_seal"],
        "wave_count": len(waves),
        "inventory_count": len(inventory_lines),
    }


if __name__ == "__main__":
    result = verify_ep07_closure()
    print(json.dumps(result, indent=2, sort_keys=True))
