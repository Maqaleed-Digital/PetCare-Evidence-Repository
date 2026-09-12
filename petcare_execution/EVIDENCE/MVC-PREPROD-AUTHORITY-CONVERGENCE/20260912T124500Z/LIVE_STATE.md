# A0 — live preflight, verified before any edit

```
START_HEAD=e46fb5adc65ad835ea75a6d8098321bd09482b1b
PR23_STATUS=MERGED  sha=7d8a36f08339682e90d6b1c71208ffe51ff7d6a2  2026-09-12T11:26:26Z
PR24_STATUS=MERGED  sha=e46fb5adc65ad835ea75a6d8098321bd09482b1b  2026-09-12T11:32:19Z
WORKING_TREE=CLEAN
```

## Artefacts confirmed present by path

`audit_repository.py`, migration `0032`, the W0-G convergence receipt, and
`MVC-PREPROD-SPONSOR-DECISION-PACK-001` — all present.

## The three facts this lane acts on, re-verified from source

```
SEED_IDENTITIES_PRESENT=3        u-admin-001 / u-vet-001 / u-owner-001
SEED_PASSWORD_LITERAL_PRESENT=YES  petcare_api/main.py:106,108,110
REPOSITORY_VISIBILITY=PUBLIC

ROLE_VOCABULARIES_LIVE=3
  V-A  Owner / Veterinarian / Platform Admin / Partner Clinic Admin  (require_role)
  V-B  owner / veterinarian / platform_admin / partner_clinic_admin  (minted)
  V-C  owner / vet / pharmacy / admin                                (middleware)

PHARMACY_ROLE_SURFACE_PRESENT=YES
  middleware.ts:13 alias · :19 '/pharmacy' allowlist · :22 '/account' member
  app/pharmacy/page.tsx · app/onboarding/pharmacy/page.tsx
```

Nothing was inherited from the prior receipt. Each was read from current source
before it was changed.
