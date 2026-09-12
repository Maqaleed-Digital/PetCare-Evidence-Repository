-- PRE-1 · the tenant registry foundation
--
-- AUTHORED AND REHEARSED, NOT APPLIED TO ANY PRODUCTION STORE.
-- Applying this to a production database is GATE_LIVE_APPLY and Sponsor-gated.
--
-- Authority: Sponsor ruling PRE1_RULING=1-B plus
-- TENANT_REGISTRY_STATUS=REQUIRED_FOUNDATION, recorded in
-- MVC-PREPROD-SPONSOR-DECISION-PACK-001.
--
-- PRE-1 searched for an authoritative tenant and found none: no catalogue table
-- in 33 migrations, no foreign key, no governance artefact naming a tenant.
-- `tenant_id` was an unconstrained TEXT column, so a typo produced a new, empty,
-- perfectly functional scope that nothing would ever report.
--
-- Purely additive. No existing table, column or row is altered or removed, and
-- NO TENANT ROW IS CREATED — see the note at the end.
--
-- PORTABILITY (D.21). Plain SQL only.

CREATE TABLE IF NOT EXISTS tenant (
    -- The stable machine identifier, and the value every tenant_id column
    -- references. Deliberately NOT a surrogate key with a separate "tenant_key":
    -- the estate already stores this string in user_identity, app_session and
    -- audit_event, and introducing a second identifier would mean every one of
    -- those columns pointed at the wrong one of the two until each was migrated.
    tenant_id TEXT PRIMARY KEY CHECK (length(TRIM(tenant_id)) > 0),

    -- Presentation. Never an authority value, and never compared.
    display_name TEXT NOT NULL CHECK (length(TRIM(display_name)) > 0),

    status TEXT NOT NULL DEFAULT 'ACTIVE'
        CHECK (status IN ('ACTIVE', 'DISABLED')),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Disabling is recorded, never a deletion. A tenant that is removed cannot
    -- be shown to have been disabled rather than to have never existed, and its
    -- identities and audit events would lose the only thing explaining what
    -- scope they belonged to.
    disabled_at TIMESTAMP NULL,

    -- A status with no instant cannot be reconciled against anything that
    -- happened, so the two fields move together.
    CHECK (status <> 'DISABLED' OR disabled_at IS NOT NULL),
    CHECK (status <> 'ACTIVE' OR disabled_at IS NULL),
    CHECK (disabled_at IS NULL OR disabled_at >= created_at)
);

-- ---------------------------------------------------------------------------
-- Referential integrity, where the semantics support it
-- ---------------------------------------------------------------------------
--
-- NULL remains permitted on both: an identity with NO tenant assignment is the
-- legitimate state W0-C defines, failing closed downstream at require_tenant()
-- with 403 NO_TENANT_AUTHORITY. A foreign key does not constrain NULL, so the
-- governed absence survives while an invented value does not.

ALTER TABLE user_identity
    ADD CONSTRAINT fk_user_identity_tenant
    FOREIGN KEY (tenant_id) REFERENCES tenant(tenant_id);

ALTER TABLE app_session
    ADD CONSTRAINT fk_app_session_tenant
    FOREIGN KEY (tenant_id) REFERENCES tenant(tenant_id);

-- ---------------------------------------------------------------------------
-- audit_event deliberately has NO foreign key
-- ---------------------------------------------------------------------------
--
-- Its tenant_id is TEXT NOT NULL and legitimately holds `UNATTRIBUTED` for
-- events from the unauthenticated UI probe — a surface that, by governed
-- decision, accepts events from callers with no session. Adding a foreign key
-- would require an `UNATTRIBUTED` row in this table, i.e. a fake tenant that
-- every unauthenticated probe event would then appear to belong to.
--
-- TENANT-09 forbids exactly that, and the instruction is explicit: do not force
-- a fake tenant merely to satisfy a foreign key. The audit log's tenant
-- semantics are therefore enforced in the serving path, and the sentinel is
-- asserted NOT to be a usable scope by test_unattributed_is_not_a_real_scope.
--
-- Recorded rather than deferred silently:
--   AUDIT_EVENT_TENANT_FK=ABSENT_BY_DESIGN

-- ---------------------------------------------------------------------------
-- NO ROWS ARE CREATED
-- ---------------------------------------------------------------------------
--
-- TENANT_ROWS_CREATED=0. Not `tenant_jeddah_001`, not `tenant_riyadh_001` —
-- those appear only in EP-05/EP-06 test fixtures and no governance record
-- establishes either. Promoting a value whose authority is a file under tests/
-- would afterwards be indistinguishable from one the Sponsor chose.
--
-- The registry is safe empty: every tenant column is NULLable, so an estate with
-- no tenants has no identity that cannot exist. Creating a production tenant is
-- a Sponsor act and is not authorised by this foundation.
