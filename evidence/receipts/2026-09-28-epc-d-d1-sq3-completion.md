# MVC-EPC-D-001 v1.5 · Lane D · unit D1 — SQ-3 completion (all fifteen operations served), 2026-09-28

```
LANE=D   UNIT=D1   BASE=525e849704fa96cb70e348c53f88ed0ca1b923e9 (D0 merged, PR #82)   BRANCH=lane-d/d1-sq3-completion
AUTHORITY=Sponsor act MVC-SQ3-NFR08-STEP-UP-001 sha256 16efd2330f4b04e15aaf7cc04684897b7bd958feeb88c23a4133794e22f585cc
RESULT: NOT_CURRENTLY_SERVED=[] (was 4, 5, 11, 12, 13, 14, 15)   ACCEPTANCE_COUNTS=UNCHANGED (2/16, 42/68, 3/13)
MIGRATIONS 59 -> 60 (0055)   SERVED ROUTES 101 -> 112
```

## Operations built (step-up enforced by the existing SQ-3 middleware via mfa.SQ3_OPERATIONS — extended, never weakened)
| SQ-3 | Route | Class | Rules |
|---|---|---|---|
| #4 sign medical record | POST /api/pets/{pet_id}/medical-records/{record_id}/sign | normal | veterinarian with live practitioner authority; pet in session tenant; signs once (409 after); content sha256 bound; DB trigger makes a signed record immutable (UPDATE/DELETE refused) |
| #5 change role | POST /api/admin/identities/{user_id}/role | always-fresh | tenant admin; same tenant only; never own role; platform_admin conferred only by platform_admin; role-only write (`set_role`, cannot touch tenant); every subject session revoked; audited `a->b` |
| #11 personal-data export | GET /api/me/export | normal | caller's own data as an attachment (identity, language, owned pets + records, own orders); no password hash, MFA secret, code, ciphertext or session |
| #12 payout details | PUT /api/admin/tenant/payout-details | always-fresh | tenant admin; method BANK_TRANSFER; schedule WEEKLY/BIWEEKLY/MONTHLY; minimum in halalas |
| #13 bank details | PUT /api/admin/tenant/bank-details | always-fresh | tenant admin; Saudi IBAN (ISO 13616 mod-97); AES-GCM ciphertext only (key via governed secret provider, 503 if absent); reads masked; never logged or audited in clear |
| #14 issue credentials | POST /api/admin/credentials | normal | tenant admin; role the admin may confer; 1–30 days; shown once; stored as `sha256:<hex>` in invite_code; single use at /api/auth/register |
| #15 issue API keys | POST /api/admin/api-keys | normal | platform admin; shown once; stored as sha256 only; listed by 12-char prefix; revocable |
Also added (declared NOT sensitive in mfa.DECLARED_NOT_SENSITIVE, each with its reason): GET payout-details, GET
bank-details (masked), GET api-keys (metadata), POST api-keys/{key_id}/revoke.

ADDED ROUTES (D4): POST /api/pets/{pet_id}/medical-records/{record_id}/sign · POST /api/admin/identities/{user_id}/role ·
GET /api/me/export · PUT, GET /api/admin/tenant/payout-details · PUT, GET /api/admin/tenant/bank-details ·
POST /api/admin/credentials · POST, GET /api/admin/api-keys · POST /api/admin/api-keys/{key_id}/revoke.

## Findings
- D1-INVITE-CODE-LOGGED (X6, fixed): /api/auth/register logged the raw invite code (a credential) in four auth-log lines;
  they now carry `invite_ref` = "inv:" + 12 hex of its sha256.
- D1-U28-TEST-EXTENDED: `test_nfr08_sq3.py::test_every_mapped_sq3_operation_is_served_and_no_unmapped_sensitive_route_exists`
  (NFR-08 evidence node) asserted the seven unserved items; D1 is the instructed extension, so the assertion is now
  `NOT_CURRENTLY_SERVED == ()`, and the route-name guard accepts a match only if MAPPED or DECLARED not sensitive (every
  declaration must be a served route and not also mapped). The guard is no weaker. NFR-08 evidence node ids unchanged.
- D1-ROLE-WRITE-WAS-WHOLE-IDENTITY (fixed before PR): the first cut wrote the whole identity (`identities.upsert`);
  the existing structural guard `test_no_route_other_than_the_governed_one_writes_tenant_membership` refused it. Now a
  role-only `set_role(user_id, role, tenant_id=…)`.
- D1-PAYOUT-ALWAYS-FRESH-TEST-GAP (fixed before PR): perturbation P-D1-PAYOUT-NOT-ALWAYS-FRESH was first VACUOUS — the
  test proved #13 but not #12 on its own. The test now refuses a second #12 without a new step-up.
- D-LIMITS-GENERATED-ARTEFACTS: the instrument's LIMITS list requirements/**, while D4 says served routes may grow. The
  generated inventories requirements/served_routes.json and requirements/status.json (served_route_count only) are
  regenerated, as `tests/governance/test_register_status.py` requires; requirements/acceptance/**, register.yaml and
  authority/** are byte-identical. No FR/NFR status changes.

## Tests
petcare_api/tests/test_epc_d1_sq3_completion.py (6, served_app + mfa_enforced) · test_epc_d1_sq3_postgres.py (DB trigger
refuses UPDATE/DELETE of a signed record; one of eight concurrent signs wins; IBAN ciphertext and key sha256 only) ·
test_nfr08_sq3.py every-role challenge now covers the seven new operations.

## Perturbations — evidence/replay/2026-09-28-epc-d/perturb_epc_d_d1.py
P-D1-SIGN-NO-STEP-UP · P-D1-SIGN-TWICE · P-D1-PG-SIGNED-RECORD-MUTABLE · P-D1-ROLE-NOT-ALWAYS-FRESH · P-D1-ROLE-SESSIONS-KEPT ·
P-D1-ROLE-SELF-CHANGE · P-D1-EXPORT-NO-STEP-UP · P-D1-EXPORT-LEAKS-PASSWORD-HASH · P-D1-BANK-IBAN-RETURNED ·
P-D1-IBAN-CHECKSUM-SKIPPED · P-D1-PAYOUT-NOT-ALWAYS-FRESH · P-D1-CREDENTIAL-STORED-RAW · P-D1-CREDENTIAL-LOGGED ·
P-D1-API-KEY-STORED-RAW · P-D1-API-KEY-ANY-ADMIN → ARMED=15 VACUOUS=0.
