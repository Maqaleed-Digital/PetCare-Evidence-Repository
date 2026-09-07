-- W0-I · professional authority, separate from device sealing authority
--
-- AUTHORED, NOT APPLIED. CP-2 W0-I: LIVE_GATE=NO. CP-2 §4 authorizes migration
-- design and authoring; applying is GATE_LIVE_APPLY and Sponsor-gated.
--
-- BRD V3.2 §28 / PRD-14.

-- Authority is TIME-BOUNDED, not a flag on a user row.
--
-- T-PROF-01 denies attesting a clinical record as an identity that did not hold
-- authority AT THAT TIME. A boolean column cannot answer that: it knows only the
-- present, so a revoked veterinarian would retroactively appear never to have
-- been authorised, and a newly granted one would appear to have always been.
-- effective_from / revoked_at make the question answerable.
CREATE TABLE IF NOT EXISTS professional_authority_grant (
    grant_id TEXT PRIMARY KEY,
    actor_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    clinic_id TEXT NULL,
    professional_class TEXT NOT NULL
        CHECK (professional_class IN ('VETERINARIAN', 'VETERINARY_NURSE')),
    effective_from TIMESTAMP NOT NULL,
    revoked_at TIMESTAMP NULL,

    -- NULL granted_by is meaningful, not missing data: it is the recorded fact
    -- that a one-vet practice had no second principal. The CHECK below makes the
    -- two cases mutually exclusive so the absence can never be silent.
    granted_by TEXT NULL,
    grant_reason TEXT NOT NULL CHECK (length(grant_reason) > 0),
    sole_practitioner_bootstrap BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- PRD-14 / T-PROF-03: a bootstrap is ALLOWED and RECORDED, never silent.
    -- Exactly one of the two shapes is legal:
    --   ordinary grant  -> granted_by present, bootstrap FALSE
    --   bootstrap       -> granted_by absent,  bootstrap TRUE
    -- A grant with no principal that is not marked as a bootstrap is precisely
    -- the silent exception §28 forbids, and cannot be stored.
    CHECK (
        (sole_practitioner_bootstrap = FALSE AND granted_by IS NOT NULL)
        OR
        (sole_practitioner_bootstrap = TRUE  AND granted_by IS NULL)
    ),

    -- Revocation is forward-looking; it never precedes the grant.
    CHECK (revoked_at IS NULL OR revoked_at >= effective_from)
);

CREATE INDEX IF NOT EXISTS idx_prof_authority_actor_window
    ON professional_authority_grant (actor_id, effective_from, revoked_at);

CREATE INDEX IF NOT EXISTS idx_prof_authority_bootstrap
    ON professional_authority_grant (sole_practitioner_bootstrap)
    WHERE sole_practitioner_bootstrap = TRUE;

-- Attestation of a clinical record by a person holding authority at the time.
CREATE TABLE IF NOT EXISTS clinical_record_attestation (
    attestation_id TEXT PRIMARY KEY,
    record_id TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    professional_class TEXT NOT NULL,
    -- The instant of the CLINICAL ACT, which is what authority is checked
    -- against — not the instant of attestation. Checking the latter would let a
    -- newly authorised vet attest records from before they held authority.
    occurred_at TIMESTAMP NOT NULL,
    attested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    grant_id TEXT NOT NULL REFERENCES professional_authority_grant(grant_id)
);

CREATE INDEX IF NOT EXISTS idx_attestation_record
    ON clinical_record_attestation (record_id);

-- DELIBERATELY NOT MODELLED HERE: device sealing authority.
--
-- §28 requires the two to be separate and not conflated. Putting a device's
-- sealing authority in this table — or adding a device_id column to a grant —
-- would make professional authority derivable from a device, which T-PROF-02
-- denies. Sealing answers "was this record altered after it was written";
-- professional authority answers "was the person who wrote it entitled to".
-- A device can guarantee the first and can say nothing about the second.
