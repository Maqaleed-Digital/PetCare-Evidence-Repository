-- 0035 — the single-use first-`platform_admin` genesis act.
--
-- Sponsor ruling of 12 September 2026,
-- MVC-GENESIS-PLATFORM-ADMIN-001 (`MYVETICARE FIRST PLATFORM ADMINISTRATOR
-- GENESIS AUTHORITY`):
--
--   GENESIS_AUTHORITY=SINGLE_USE
--   GENERAL_PLATFORM_ADMIN_ELEVATION_AUTHORITY=NOT_AUTHORIZED
--   GENESIS_REUSE=PROHIBITED
--   SECOND_GENESIS_ATTEMPT=MUST_FAIL_CLOSED
--
-- The ruling exists because the governed system requires an existing
-- `platform_admin` before tenant membership can be administered, while
-- RATIFICATION-002 withholds every ordinary role-creation and role-elevation
-- authority. That is a genuine deadlock, and this migration provides the
-- narrowest possible structural exit from it.
--
-- THIS MIGRATION CREATES NO IDENTITY AND CONSUMES NO AUTHORITY.
-- It establishes the shape. `PLATFORM_ADMIN_ROWS_CREATED=0`,
-- `GENESIS_CONSUMED=NO`. Applying the chain is not the genesis act, and
-- PRODUCTION_GENESIS_EXECUTION=NOT_AUTHORIZED_BY_THIS_RULING.
--
-- Nothing here is irreversible: no DROP TABLE, no TRUNCATE, no row deletion.
--
-- `GENESIS` here is the PROVENANCE of an identity. It is unrelated to
-- `AUDIT_CHAIN_GENESIS`, the marker the audit hash chain starts from in 0032 —
-- same word, different subject, and neither reads the other.

-- ---------------------------------------------------------------------------
-- 1 · `GENESIS` provenance
-- ---------------------------------------------------------------------------
--
-- The first administrator came from none of the three existing origins. `SEED`
-- is the category PRE-1 discarded as development artefacts whose password was a
-- published literal; `REGISTRATION` is the invite-gated public path, which
-- grants no elevated role by design; `IDENTITY_MIGRATION` describes a row
-- traced to a source record that does not exist here.
--
-- Recording the genesis identity as any of them would misdescribe how the
-- highest privilege in the system came to exist — and §4 requires the genesis
-- event to be identifiable AS a genesis event rather than disguised as an
-- ordinary one. A row that cannot be told apart from a seed is a row whose
-- authority cannot be audited.
--
-- The constraint is located by its definition rather than by a generated name,
-- so this applies cleanly whatever PostgreSQL called 0031's inline CHECK.
DO $$
DECLARE
    target_constraint TEXT;
BEGIN
    SELECT con.conname INTO target_constraint
    FROM pg_constraint con
    JOIN pg_class rel ON rel.oid = con.conrelid
    WHERE rel.relname = 'user_identity'
      AND con.contype = 'c'
      AND pg_get_constraintdef(con.oid) LIKE '%REGISTRATION%'
      AND pg_get_constraintdef(con.oid) LIKE '%IDENTITY_MIGRATION%'
      AND pg_get_constraintdef(con.oid) NOT LIKE '%tenant_id%'
      AND pg_get_constraintdef(con.oid) NOT LIKE '%source_record_id%'
    LIMIT 1;

    IF target_constraint IS NULL THEN
        RAISE EXCEPTION
            'the user_identity provenance CHECK from migration 0031 was not found; refusing to widen a constraint that is not there';
    END IF;

    EXECUTE format(
        'ALTER TABLE user_identity DROP CONSTRAINT %I', target_constraint);
END
$$;

ALTER TABLE user_identity
    ADD CONSTRAINT user_identity_provenance_check CHECK (
        provenance IN ('SEED', 'REGISTRATION', 'IDENTITY_MIGRATION', 'GENESIS')
    );

-- At most ONE identity may ever carry `GENESIS` provenance.
--
-- §5: *"no additional privileged identity may have been created by the genesis
-- operation"*, and §7 withholds creation of a second `platform_admin`. Enforced
-- here rather than only in the service, because the ruling requires the
-- single-use property to rest on *"durable production state, not operator
-- memory or documentation alone"* — and a check that lives only in application
-- code is bypassed by the next caller who does not use it.
CREATE UNIQUE INDEX IF NOT EXISTS uq_user_identity_single_genesis
    ON user_identity (provenance)
    WHERE provenance = 'GENESIS';

-- ---------------------------------------------------------------------------
-- 2 · The genesis authority consumption record
-- ---------------------------------------------------------------------------
--
-- §5: *"the genesis authority must be consumable exactly once… After successful
-- execution the genesis authority is marked consumed, the genesis path becomes
-- unavailable for subsequent use, a second invocation must fail closed."*
--
-- `singleton` is a one-valued primary key, so the table can hold at most one
-- row by construction. A counter column would be a value somebody could reset;
-- a row that cannot have a sibling is a state that cannot be reset without an
-- explicit, visible statement against a table named for the authority it holds.
CREATE TABLE IF NOT EXISTS platform_admin_genesis (
    singleton BOOLEAN PRIMARY KEY DEFAULT TRUE CHECK (singleton),

    -- The identity the authority was consumed to establish. Named so the record
    -- answers §5's *"verify that the intended first platform administrator
    -- exists"* without depending on a log.
    target_user_id TEXT NOT NULL
        REFERENCES user_identity(user_id),

    -- The role the governed procedure fixed. Stored, and constrained to the one
    -- value the ruling permits: §2 forbids the procedure from being *"capable of
    -- creating any other privileged role"*, so a record admitting another value
    -- would describe an act the ruling does not authorize.
    granted_role TEXT NOT NULL CHECK (granted_role = 'platform_admin'),

    -- §4: the governing Sponsor ruling, recorded with the act rather than
    -- alongside it. An act whose authority is cited only in a separate document
    -- is an act whose authority can be lost.
    ruling_reference TEXT NOT NULL
        CHECK (length(TRIM(ruling_reference)) > 0),

    -- §4: the governed audit record for this act. NOT NULL is the transactional
    -- half of §6 — a consumption record can never name a missing audit event.
    audit_event_id TEXT NOT NULL
        CHECK (length(TRIM(audit_event_id)) > 0),

    -- §4: the execution timestamp.
    consumed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
