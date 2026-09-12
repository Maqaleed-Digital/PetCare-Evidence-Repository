-- PRE-2 / CONF-01 · narrow the stored role catalogue to canonical machine IDs
--
-- AUTHORED AND REHEARSED, NOT APPLIED TO ANY PRODUCTION STORE.
-- Applying this to a production database is GATE_LIVE_APPLY and Sponsor-gated.
--
-- Authority: Sponsor ruling PRE2_RULING=2-C, recorded in
-- MVC-PREPROD-SPONSOR-DECISION-PACK-001 — "machine role IDs are the sole
-- authorization authority; display/localized labels are presentation only".
-- Mirrors petcare_api/roles.py ALLOWED_ROLES.
--
-- Historical migrations are NOT edited. 0031 admitted eight spellings because
-- two vocabularies were in live use and choosing between them was a Sponsor
-- product act that had not been taken. It has now been taken, so the catalogue
-- narrows here, additively, in its own file.
--
-- PORTABILITY (D.21). Plain SQL only.

-- ---------------------------------------------------------------------------
-- Why replacing a CHECK rather than adding one
-- ---------------------------------------------------------------------------
--
-- A second, narrower CHECK alongside the original would work — both must hold,
-- so the narrower one wins. It would also leave the repository stating two
-- different catalogues in two places, and the next reader would have to derive
-- the effective set by intersecting them. The constraint is replaced so that
-- the schema says exactly one thing about what a role may be.
--
-- ADD CONSTRAINT validates existing rows and FAILS if any violate it. That is
-- the intended behaviour: a row holding a display spelling is an identity whose
-- authority this ruling has just changed, and it must be seen and migrated
-- deliberately rather than silently retained. There are no such rows in an
-- unprovisioned estate; if the apply fails, that failure is the finding.

ALTER TABLE user_identity DROP CONSTRAINT IF EXISTS user_identity_role_check;
ALTER TABLE user_identity ADD CONSTRAINT user_identity_role_check
    CHECK (role IN ('platform_admin', 'partner_clinic_admin', 'veterinarian', 'owner'));

ALTER TABLE invite_code DROP CONSTRAINT IF EXISTS invite_code_allowed_role_check;
ALTER TABLE invite_code ADD CONSTRAINT invite_code_allowed_role_check
    CHECK (allowed_role IN ('platform_admin', 'partner_clinic_admin', 'veterinarian', 'owner'));

ALTER TABLE app_session DROP CONSTRAINT IF EXISTS app_session_role_check;
ALTER TABLE app_session ADD CONSTRAINT app_session_role_check
    CHECK (role IN ('platform_admin', 'partner_clinic_admin', 'veterinarian', 'owner'));

-- ---------------------------------------------------------------------------
-- The retired role, and `pharmacy`
-- ---------------------------------------------------------------------------
--
-- Both are refused by ABSENCE from the lists above, never by being named. A
-- denylist would have to write the retired literal into the repository, and a
-- guard indistinguishable from the defect it guards against is not a guard.
--
-- PHARMACY_ROLE=REMOVE: `pharmacy` is not an authorization principal, so it is
-- not a storable role. PHARMACY_DOMAIN_CAPABILITIES=RETAIN_PENDING_ROLE_REBINDING
-- concerns product capability, which lives in routes and surfaces rather than in
-- this catalogue — nothing in this file removes a capability.
