-- W0-F · persistent identity, invite codes and server-side sessions
--
-- AUTHORED AND REHEARSED, NOT APPLIED TO ANY PRODUCTION STORE.
-- CP-2 §4 authorises migration design, authoring and non-production rehearsal;
-- applying this to a production database is GATE_LIVE_APPLY and Sponsor-gated.
--
-- Authority: MVC-W0F-DATA-STORE-DECISION-001 (relational system of record),
-- MVC-W0F-IDENTITY-MIGRATION-PLAN-001 §2 (target schema),
-- MVC-W0F-ADDENDUM-001 §4 item 1, CP-2 Wave-0 W0-F.
--
-- Purely additive: no existing table, column or row is altered or removed.
-- Reversal is by removing the four tables created here; nothing that existed
-- before this migration is touched, so reversal restores the prior state
-- exactly.
--
-- PORTABILITY (D.21). Plain SQL only. No provider-proprietary type, extension
-- or function appears below, so the mandatory KSA move replays this file
-- unchanged against the approved target.

-- ---------------------------------------------------------------------------
-- Identity
-- ---------------------------------------------------------------------------
--
-- Today identity is `_users`, a dict re-seeded at every process start. The
-- migration plan records the consequence plainly: there are no persisted
-- credentials, so this is not a data move — it is a change of where future
-- identity is written. Taken now it is close to free; taken after production
-- identity exists it is a credential migration.
CREATE TABLE IF NOT EXISTS user_identity (
    user_id TEXT PRIMARY KEY,

    -- UNIQUE is the structural half of MIG-06. A duplicate source identity must
    -- not silently overwrite an existing row, and a uniqueness constraint makes
    -- that unrepresentable rather than merely unlikely — the migration tool's
    -- duplicate detection and this constraint fail in the same direction.
    email TEXT NOT NULL UNIQUE CHECK (length(TRIM(email)) > 0),

    -- Opaque. The migration never has access to a plaintext password
    -- (MVC-W0F-IDENTITY-MIGRATION-PLAN-001 §7) and nothing here re-hashes.
    password_hash TEXT NOT NULL CHECK (length(password_hash) > 0),

    -- The role catalogue, stated positively. The retired role is refused by
    -- being absent, never by being named: naming it would reintroduce the
    -- literal that MVC-RETIRED-ROLE-CUSTODY-001 requires to be absent from live
    -- source, and a guard indistinguishable from the defect it guards against
    -- is not a guard. Mirrors petcare_api/roles.py VALID_ROLES.
    -- Changing this catalogue is a Sponsor product act (CP-2 W0-D, invariant I-5).
    role TEXT NOT NULL CHECK (
        role IN (
            -- Serving spellings, minted by seed_user and invite-gated
            -- registration.
            'owner', 'veterinarian', 'partner_clinic_admin', 'platform_admin',
            -- Display spellings, which require_role() in the serving layer is
            -- what actually accepts. BOTH are in live use; that divergence is
            -- recorded authority conflict CONF-01 and is NOT resolved by this
            -- migration. Admitting only one vocabulary here would decide it,
            -- and deciding it changes who may act — a Sponsor product act.
            'Owner', 'Veterinarian', 'Partner Clinic Admin', 'Platform Admin'
        )
    ),

    -- NULLable, and that is deliberate. W0-C establishes tenant as an attribute
    -- of the identity, established server-side — and `seed_user` legitimately
    -- creates an identity with no tenant assignment, which fails closed
    -- downstream at require_tenant() with 403 NO_TENANT_AUTHORITY.
    --
    -- What is NOT legitimate is the empty string: that is not "no tenant", it is
    -- a tenant whose value was lost, and storing it would key rows on a value
    -- that can later collide. The CHECK makes the malformed case
    -- unrepresentable while leaving the meaningful absence expressible — the
    -- same distinction the in-memory session store already enforces.
    tenant_id TEXT NULL CHECK (tenant_id IS NULL OR length(TRIM(tenant_id)) > 0),

    full_name TEXT NOT NULL,

    -- How this row came to exist. Not decoration: the CHECK below depends on it.
    provenance TEXT NOT NULL CHECK (
        provenance IN ('SEED', 'REGISTRATION', 'IDENTITY_MIGRATION')
    ),
    -- The source identifier, for rows that came from the identity migration.
    -- Lets reconciliation prove every migrated row traces to a source record and
    -- that no row was invented.
    source_record_id TEXT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Disabling is recorded, never a removal: an identity that is gone cannot be
    -- shown to have been disabled rather than to have never existed.
    disabled_at TIMESTAMP NULL,

    -- MIG-05 / plan §8, enforced STRUCTURALLY rather than by the tool alone.
    --
    -- An identity whose tenant could not be resolved is quarantined, never
    -- guessed. If that rule lived only in the migration script, a later re-run,
    -- a manual insert or a repaired record could place an unresolved identity
    -- into the authoritative table, and afterwards it would be indistinguishable
    -- from a verified one. Here the database refuses it.
    --
    -- Scoped to IDENTITY_MIGRATION on purpose: the seeded tenantless identity is
    -- a real, governed state and must remain expressible.
    CHECK (provenance <> 'IDENTITY_MIGRATION' OR tenant_id IS NOT NULL),

    -- A migrated row without a source record cannot be reconciled against
    -- anything, which is the same defect as an invented row.
    CHECK (provenance <> 'IDENTITY_MIGRATION' OR source_record_id IS NOT NULL),

    CHECK (disabled_at IS NULL OR disabled_at >= created_at)
);

CREATE INDEX IF NOT EXISTS idx_user_identity_tenant
    ON user_identity (tenant_id);

-- ---------------------------------------------------------------------------
-- Invite codes
-- ---------------------------------------------------------------------------
--
-- Persisted because consumption must SURVIVE a restart. `_invite_codes` is
-- re-seeded at every process start, so a consumed pilot code becomes unconsumed
-- whenever the process restarts and registration re-opens on a code that was
-- already spent. That is a live authorization defect, not merely missing
-- durability, which is why this table is PERSIST_NOW and not deferred.
CREATE TABLE IF NOT EXISTS invite_code (
    code TEXT PRIMARY KEY CHECK (length(TRIM(code)) > 0),
    allowed_role TEXT NOT NULL CHECK (
        allowed_role IN (
            'owner', 'veterinarian', 'partner_clinic_admin', 'platform_admin',
            'Owner', 'Veterinarian', 'Partner Clinic Admin', 'Platform Admin'
        )
    ),
    tenant_id TEXT NULL CHECK (tenant_id IS NULL OR length(TRIM(tenant_id)) > 0),
    expires_at TIMESTAMP NULL,
    consumed_at TIMESTAMP NULL,
    consumed_by TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Consumption is one fact with two fields. A code marked consumed by nobody,
    -- or attributed to somebody without being consumed, is a half-written
    -- record; either shape would let an audit reach a confident wrong answer
    -- about who used a code.
    CHECK (
        (consumed_at IS NULL AND consumed_by IS NULL)
        OR (consumed_at IS NOT NULL AND consumed_by IS NOT NULL)
    )
);

-- ---------------------------------------------------------------------------
-- Sessions (W0-F AC-7)
-- ---------------------------------------------------------------------------
--
-- Named app_session rather than session: `session` is heavily overloaded in
-- both SQL tooling and this estate's own vocabulary (a consultation session is
-- a different thing entirely), and a table whose name is ambiguous in a
-- clinical system gets joined wrongly eventually.
CREATE TABLE IF NOT EXISTS app_session (
    session_id TEXT PRIMARY KEY,

    -- A session must belong to an identity that exists. Without the reference a
    -- session could outlive the identity it authorises, and an orphaned session
    -- row is indistinguishable from a valid one at lookup time.
    user_id TEXT NOT NULL REFERENCES user_identity(user_id),

    -- Same NULL-vs-blank distinction as user_identity, and for the same reason.
    -- The lookup is tenant-scoped, so a blank tenant here would be a session
    -- keyed on a colliding value.
    tenant_id TEXT NULL CHECK (tenant_id IS NULL OR length(TRIM(tenant_id)) > 0),

    role TEXT NOT NULL CHECK (
        role IN (
            -- Serving spellings, minted by seed_user and invite-gated
            -- registration.
            'owner', 'veterinarian', 'partner_clinic_admin', 'platform_admin',
            -- Display spellings, which require_role() in the serving layer is
            -- what actually accepts. BOTH are in live use; that divergence is
            -- recorded authority conflict CONF-01 and is NOT resolved by this
            -- migration. Admitting only one vocabulary here would decide it,
            -- and deciding it changes who may act — a Sponsor product act.
            'Owner', 'Veterinarian', 'Partner Clinic Admin', 'Platform Admin'
        )
    ),

    issued_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,

    -- Revocation writes a timestamp; the row stays. Removing it would erase the
    -- difference between "this session was revoked at 14:02" and "this session
    -- never existed", and the first is the one an incident review needs.
    revoked_at TIMESTAMP NULL,
    revocation_reason TEXT NULL,

    -- A session that expires at or before it was issued is dead on arrival, and
    -- would be a silently useless record rather than an error.
    CHECK (expires_at > issued_at),
    CHECK (revoked_at IS NULL OR revoked_at >= issued_at)
);

-- The lookup the serving path performs on every authenticated request is by
-- primary key, so it needs no index. This one serves revoke_all_for_user, which
-- is the operation that replaces key rotation for the common case and must not
-- degrade into a full scan as the table grows.
CREATE INDEX IF NOT EXISTS idx_app_session_user_tenant
    ON app_session (user_id, tenant_id);

-- Expired-session housekeeping reads by expiry.
CREATE INDEX IF NOT EXISTS idx_app_session_expires
    ON app_session (expires_at);

-- ---------------------------------------------------------------------------
-- Identity migration quarantine
-- ---------------------------------------------------------------------------
--
-- Plan §8. Records that cannot be deterministically mapped are quarantined,
-- never guessed. They fail closed: an identity that did not migrate cannot
-- authenticate, which is the safe direction.
--
-- A separate table rather than a status column on user_identity, deliberately.
-- A quarantined identity living in the authoritative table behind a flag is one
-- forgotten WHERE clause away from being treated as resolved, and the resulting
-- row would look exactly like a verified one.
CREATE TABLE IF NOT EXISTS identity_migration_quarantine (
    source_record_id TEXT PRIMARY KEY,
    reason TEXT NOT NULL CHECK (
        reason IN (
            'UNRESOLVED_NO_TENANT',
            'UNRESOLVED_UNKNOWN_ROLE',
            'UNRESOLVED_DUPLICATE',
            'UNRESOLVED_MALFORMED_RECORD'
        )
    ),
    -- Recorded verbatim, including values the catalogue rejects — that is the
    -- point of quarantine. No CHECK constrains them to the role catalogue: an
    -- unknown role is precisely what is being recorded.
    source_role TEXT NULL,
    source_tenant TEXT NULL,
    source_email TEXT NULL,
    status TEXT NOT NULL DEFAULT 'UNRESOLVED' CHECK (
        status IN ('UNRESOLVED', 'RESOLVED_MIGRATED', 'RESOLVED_REJECTED')
    ),
    resolution_note TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Resolution is manual and recorded (plan §8). A row that changed status
    -- without a note records that somebody decided, and nothing about what.
    CHECK (status = 'UNRESOLVED' OR resolution_note IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_identity_quarantine_status
    ON identity_migration_quarantine (status);
