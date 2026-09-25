/**
 * FR-13 (MVC-BUILD-RUNNER-001 U8) — the inventory view refreshes itself.
 *
 * Ratified AC-FR-13-01 (ACCEPT_WITH_THRESHOLD, REAL_TIME_BOUND=5_SECONDS): a committed
 * stock change becomes visible to another authorised session of the same tenant with
 * p95 <= 5 seconds. /pharmacy/inventory re-reads the served stock every
 * INVENTORY_REFRESH_MS, so the UI's share of that latency is bounded by this interval;
 * the server's share is measured in petcare_api/tests/test_inventory.py.
 */
export const INVENTORY_REFRESH_MS = 2000

export const SUPPLY_CLASSES = ['GENERAL', 'OTC', 'POM', 'RESTRICTED', 'CONTROLLED'] as const
export type SupplyClass = (typeof SUPPLY_CLASSES)[number]

/** MVC-PHARM-001 §5: veterinarian-only until counsel (L-2). The server enforces it; the UI only labels it. */
export const VETERINARIAN_ONLY: readonly SupplyClass[] = ['POM', 'RESTRICTED', 'CONTROLLED']

export type StockLine = { product_id: string; batch: string; quantity: number; supply_class: SupplyClass }
export type LocationStock = { location_id: string; name: string; stock: StockLine[] }
