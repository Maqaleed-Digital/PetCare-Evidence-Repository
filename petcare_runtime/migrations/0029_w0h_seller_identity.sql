-- W0-H · seller/taxpayer identity on commercial records
--
-- AUTHORED, NOT APPLIED. CP-2 W0-H: LIVE_GATE=NO for design, YES for any apply.
-- CP-2 §4 authorizes migration design and authoring; applying this is
-- GATE_LIVE_APPLY and Sponsor-gated.
--
-- Annex K §K.2 REQ-FIN-S1: seller/taxpayer identity is an attribute of the
-- transaction record, set at creation from the clinic's own registration
-- record, and immutable thereafter.
--
-- EP-07 SEAL. partner_orders belongs to the sealed marketplace domain. This
-- migration adds ADDITIVE COLUMNS ONLY. No catalogue, contract, pricing or
-- settlement logic is reimplemented, and no sealed module is modified. Adding an
-- attribute to a record is not re-owning the domain that manages it.

-- ---------------------------------------------------------------------------
-- REQ-FIN-S1 · seller identity, set at creation, immutable thereafter
-- ---------------------------------------------------------------------------
-- NULLable on introduction. See the classification note below: enforcement is
-- the last step, never the first.
ALTER TABLE partner_orders ADD COLUMN seller_id TEXT NULL;
ALTER TABLE partner_orders ADD COLUMN seller_registration_id TEXT NULL;
ALTER TABLE partner_orders ADD COLUMN seller_identity_source TEXT NULL;

CREATE INDEX IF NOT EXISTS idx_partner_orders_seller
    ON partner_orders (seller_id);

-- ---------------------------------------------------------------------------
-- REQ-FIN-G1..G3 · gross is a fact; deductions are separate movements
-- ---------------------------------------------------------------------------
-- Gross consideration is the total payable by the owner, exclusive of every
-- platform fee, commission, payment cost and deduction. It is recorded once.
ALTER TABLE partner_orders ADD COLUMN gross_value NUMERIC(12,2) NULL
    CHECK (gross_value IS NULL OR gross_value >= 0);

-- Deductions REFERENCE the gross sale. They never mutate, replace or net
-- against it. A deduction is a row here, never a subtraction there — which is
-- why this is a separate table and not a `net_value` column.
--
-- Net settlement is DERIVED (gross less referenced deductions) and is
-- deliberately NOT stored: REQ-FIN-G3 forbids holding it as an authoritative
-- fact. Any future `net_value` column would violate that requirement.
CREATE TABLE IF NOT EXISTS commercial_deduction_movement (
    deduction_movement_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL REFERENCES partner_orders(order_id),
    deduction_type TEXT NOT NULL
        CHECK (deduction_type IN (
            'PLATFORM_FEE', 'COMMISSION', 'PAYMENT_PROCESSING',
            'REFUND', 'CHARGEBACK', 'OTHER'
        )),
    amount NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
    currency TEXT NOT NULL DEFAULT 'SAR',
    recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_deduction_movement_order
    ON commercial_deduction_movement (order_id);

-- ---------------------------------------------------------------------------
-- PRE-EXISTING ROWS — deterministic where provable, UNRESOLVED otherwise
-- ---------------------------------------------------------------------------
-- CP-2 W0-H MIGRATION_DESIGN: additive first -> deterministic classification
-- where provable -> rows that cannot be deterministically classified are
-- recorded as UNRESOLVED, never guessed -> validate -> only then enforce NOT
-- NULL if safe.
--
-- A pre-existing order carries no seller identity, and seller identity cannot be
-- inferred from payment routing: REQ-FIN-S3 states that the identity of whoever
-- receives funds first must never determine seller identity. Inferring a seller
-- from the routed partner would be precisely the reasoning that requirement
-- forbids, and it would be invisible once written.
--
-- Rows whose seller is not provable from a clinic registration record are
-- therefore marked UNRESOLVED and left for a recorded decision.
UPDATE partner_orders
   SET seller_identity_source = 'UNRESOLVED'
 WHERE seller_id IS NULL;

-- NOT ENFORCED YET, and deliberately so. NOT NULL here would fail closed
-- against every historical row this migration has just marked UNRESOLVED.
--
--   ALTER TABLE partner_orders ALTER COLUMN seller_id SET NOT NULL;
--
-- Precondition: every writer populates seller identity at creation from the
-- clinic registration record, AND the UNRESOLVED backlog has a Sponsor
-- disposition. Only then is enforcement safe.
--
-- IMMUTABILITY (REQ-FIN-S1) is enforced structurally, not by a CHECK
-- constraint: tests/governance/test_seller_identity_write_authority.py asserts
-- that no payment, settlement, marketplace or fee-collection component holds
-- write authority over the field at all. Annex K §K.2 requires exactly that —
-- "enforced structurally, not by convention or code review".
