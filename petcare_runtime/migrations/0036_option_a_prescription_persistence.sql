-- Option A · durable prescriptions, their attachments and their transitions
--
-- AUTHORED AND REHEARSED, NOT APPLIED TO ANY PRODUCTION STORE.
-- Applying this to a production database is GATE_LIVE_APPLY and Sponsor-gated.
--
-- Authority: FR-14 (Pharma Care pilot, Option A). The serving layer held
-- prescriptions in `_prescriptions`, a module-level dict — the same shape W0-G
-- found in the audit log and for the same reason it was wrong there: a store
-- that dies with the process, is invisible to every other instance, and makes
-- a "prescription" a claim no second reader can confirm. A dispensing record
-- that does not survive a restart cannot be the record a regulator asks for.
--
-- Purely additive. No existing table, column or row is altered or removed.
-- Reversal is by dropping the three tables created here, in the reverse of the
-- order they appear; nothing that existed before this migration is touched.
--
-- PORTABILITY (D.21). Plain SQL only. No provider-proprietary type, extension
-- or function appears below, so the mandatory KSA move replays this file
-- unchanged against the approved target.

-- ---------------------------------------------------------------------------
-- The prescription itself
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS prescription (
    prescription_id TEXT PRIMARY KEY,

    -- Tenant is a real scope here, never a sentinel. Unlike audit_event — whose
    -- FK is ABSENT_BY_DESIGN because it legitimately holds `UNATTRIBUTED` for
    -- the unauthenticated probe — every prescription is written by an
    -- authenticated caller that has already passed require_tenant(), so there
    -- is no legitimate row whose tenant is not a registered tenant. The
    -- constraint therefore costs nothing real and makes a typo'd scope
    -- unrepresentable instead of merely unreported (the PRE-1 finding).
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),

    pet_id TEXT NOT NULL CHECK (length(TRIM(pet_id)) > 0),
    session_id TEXT NOT NULL CHECK (length(TRIM(session_id)) > 0),
    clinic_id TEXT NULL,

    -- Server-derived at issue time from the validated session, never from a
    -- request body. Stored so the prescribing professional is recoverable from
    -- the record rather than only from the audit chain.
    issuing_vet_id TEXT NOT NULL CHECK (length(TRIM(issuing_vet_id)) > 0),

    medication_name TEXT NOT NULL CHECK (length(TRIM(medication_name)) > 0),
    dosage TEXT NOT NULL CHECK (length(TRIM(dosage)) > 0),
    instructions TEXT NOT NULL CHECK (length(TRIM(instructions)) > 0),

    -- The governed lifecycle, stated positively.
    --
    -- `VET_VERIFIED` is new and it is the point of this migration. Before it,
    -- `status` went ISSUED -> DISPENSED and the dispense route's only state
    -- guard was `status == 'ISSUED'` — so a prescription was dispensable the
    -- instant it existed, and the verification step the pilot workflow is named
    -- after had no representation at all. An intermediate state that the
    -- database refuses to skip is what makes "verified before dispensed" a
    -- property of the record rather than a property of one route remembering to
    -- check.
    status TEXT NOT NULL DEFAULT 'ISSUED'
        CHECK (status IN ('ISSUED', 'VET_VERIFIED', 'DISPENSED')),

    issued_at TIMESTAMP NOT NULL,
    verified_at TIMESTAMP NULL,
    verified_by_vet_id TEXT NULL,
    dispensed_at TIMESTAMP NULL,
    dispensed_by_actor_id TEXT NULL,

    -- A status with no instant cannot be reconciled against anything that
    -- happened, and an instant with no status is a transition nobody recorded.
    -- The pairs move together, in both directions, for the same reason the
    -- tenant registry pairs `status` with `disabled_at`.
    CHECK (status <> 'ISSUED'
           OR (verified_at IS NULL AND dispensed_at IS NULL)),
    CHECK (status <> 'VET_VERIFIED'
           OR (verified_at IS NOT NULL AND dispensed_at IS NULL)),
    CHECK (status <> 'DISPENSED'
           OR (verified_at IS NOT NULL AND dispensed_at IS NOT NULL)),

    -- The actor and the instant are written by the same statement or neither is.
    CHECK ((verified_at IS NULL) = (verified_by_vet_id IS NULL)),
    CHECK ((dispensed_at IS NULL) = (dispensed_by_actor_id IS NULL)),

    -- Time runs forwards. A dispense timestamped before its verification would
    -- describe a dispense that could not have been verified.
    CHECK (verified_at IS NULL OR verified_at >= issued_at),
    CHECK (dispensed_at IS NULL OR dispensed_at >= verified_at)
);

-- Tenant-scoped listing is the pharmacy queue's only access pattern, and it is
-- always filtered by tenant before status. The index leads with tenant for the
-- same reason the predicate does.
CREATE INDEX IF NOT EXISTS idx_prescription_tenant_status
    ON prescription (tenant_id, status);

-- ---------------------------------------------------------------------------
-- The transition ledger
-- ---------------------------------------------------------------------------
--
-- `prescription` carries the CURRENT state. This carries how it got there, and
-- it is append-only by construction: there is no UPDATE path to it anywhere in
-- the serving layer, and no column that an update would have to change.
--
-- It is deliberately NOT a substitute for the audit chain. The audit chain
-- proves tamper-evidence across the whole estate; this answers a narrower
-- question the chain answers slowly — "what happened to THIS prescription" —
-- without scanning. Two stores, two questions, and neither is the other's
-- shadow copy: the chain remains authoritative if they ever disagree.
CREATE TABLE IF NOT EXISTS prescription_status_transition (
    transition_id TEXT PRIMARY KEY,
    prescription_id TEXT NOT NULL REFERENCES prescription(prescription_id),

    -- NULL only for the issuing transition, which has no prior state.
    from_status TEXT NULL
        CHECK (from_status IS NULL
               OR from_status IN ('ISSUED', 'VET_VERIFIED', 'DISPENSED')),
    to_status TEXT NOT NULL
        CHECK (to_status IN ('ISSUED', 'VET_VERIFIED', 'DISPENSED')),

    -- Server-derived. A transition attributed to a client-supplied actor would
    -- record whoever the client said it was (W0-B).
    actor_id TEXT NOT NULL CHECK (length(TRIM(actor_id)) > 0),
    actor_role TEXT NOT NULL CHECK (length(TRIM(actor_role)) > 0),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    occurred_at TIMESTAMP NOT NULL,

    -- A transition to the state it came from is not a transition.
    CHECK (from_status IS NULL OR from_status <> to_status)
);

CREATE INDEX IF NOT EXISTS idx_prescription_transition_rx
    ON prescription_status_transition (prescription_id, occurred_at);

-- ---------------------------------------------------------------------------
-- The attachment
-- ---------------------------------------------------------------------------
--
-- Metadata only. The bytes live behind the storage adapter, which in
-- non-production is a local directory and in production is an object store that
-- is NOT yet bound — see petcare_api/prescription_documents.py. Recording the
-- digest here rather than trusting the adapter means a substituted or truncated
-- object is detectable without asking the thing that stored it.
CREATE TABLE IF NOT EXISTS prescription_document (
    document_id TEXT PRIMARY KEY,
    prescription_id TEXT NOT NULL REFERENCES prescription(prescription_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),

    uploaded_by_actor_id TEXT NOT NULL
        CHECK (length(TRIM(uploaded_by_actor_id)) > 0),

    -- The caller's name for the file, kept for display only. It is never used
    -- to build a path: storage_key is server-generated precisely so a filename
    -- cannot choose where its bytes land.
    filename TEXT NOT NULL CHECK (length(TRIM(filename)) > 0),
    content_type TEXT NOT NULL CHECK (length(TRIM(content_type)) > 0),
    byte_size INTEGER NOT NULL CHECK (byte_size > 0),
    content_sha256 TEXT NOT NULL CHECK (length(content_sha256) = 64),

    -- Server-generated, opaque, and unique: two uploads cannot collide onto one
    -- object, which is how an attachment silently becomes another tenant's.
    storage_key TEXT NOT NULL UNIQUE CHECK (length(TRIM(storage_key)) > 0),

    uploaded_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_prescription_document_rx
    ON prescription_document (prescription_id);

-- ---------------------------------------------------------------------------
-- NO ROWS ARE CREATED
-- ---------------------------------------------------------------------------
--
-- PRESCRIPTION_ROWS_CREATED=0. A seeded prescription would be a clinical record
-- naming a pet, a medicine and a prescribing veterinarian that no clinician
-- wrote. The tables are safe empty.
