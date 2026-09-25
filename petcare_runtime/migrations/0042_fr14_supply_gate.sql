-- 0042 · FR-14 prescription gate by supply class (MVC-BUILD-RUNNER-001 U9)
--
-- Ratified AC-FR-14-03: the prescription gate applies to POM, RESTRICTED and CONTROLLED
-- products only; GENERAL and OTC need no prescription. A supply is a SUPPLY movement on the
-- FR-13 ledger (migration 0041). The database itself refuses a veterinarian-only supply
-- that cites no prescription, so no code path can supply POM stock without one.
--
-- Additive: one nullable column and a widened reason set. Existing rows are unaffected.

ALTER TABLE stock_movement ADD COLUMN IF NOT EXISTS prescription_id TEXT NULL;

ALTER TABLE stock_movement DROP CONSTRAINT IF EXISTS stock_movement_reason_check;
ALTER TABLE stock_movement ADD CONSTRAINT stock_movement_reason_check
    CHECK (reason IN ('RECEIPT', 'ADJUSTMENT', 'TRANSFER_OUT', 'TRANSFER_IN', 'SUPPLY'));

ALTER TABLE stock_movement DROP CONSTRAINT IF EXISTS stock_movement_supply_gate;
ALTER TABLE stock_movement ADD CONSTRAINT stock_movement_supply_gate
    CHECK (reason <> 'SUPPLY'
           OR (quantity_delta < 0
               AND (supply_class IN ('GENERAL', 'OTC') OR prescription_id IS NOT NULL)));
