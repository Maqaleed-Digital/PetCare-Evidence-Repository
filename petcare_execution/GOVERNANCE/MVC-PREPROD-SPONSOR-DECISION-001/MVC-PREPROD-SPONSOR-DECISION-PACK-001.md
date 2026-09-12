# MVC-PREPROD-SPONSOR-DECISION-PACK-001

**Status:** `RATIFIED` — `RATIFICATION-001.md`, `[SPONSOR]`, 12 September 2026.
The Ruling section below records the instruction the implementation was carried
out on; the ratification record carries the Sponsor's own statement verbatim. The proposal, options and
recommendations below are preserved verbatim as the record of what was put to the
Sponsor; nothing above the Ruling has been rewritten.
**Date:** 2026-09-12 · **Base:** `77d921e` (PR #21 + #22 merged)
**Decides:** PRE-1 (tenant assignment) and PRE-2 / CONF-01 (role authority)

One document, one ruling, two decisions. They are presented together because
acting on either alone produces a system that still cannot be used: assigning
tenants without settling role authority gives identities a scope and no routes;
settling roles without tenants gives them routes and no scope.

Nothing in this pack has been implemented. No tenant is chosen, no role is
normalised, and no authorization behaviour has changed.

Supporting evidence, measured live and not inherited:
`PRE1_TENANT_DISCOVERY.md` · `PRE2_ROLE_AUTHORITY_DISCOVERY.md` ·
`RESIDUE_REMEASURE.md`

---

## SECTION 1 — PRE-1 · tenant assignment

### The three identities

All three are created by `petcare_api/main.py` under the comment *"Seed pilot
test users (in-memory — no DB yet)"*, and all three carry **no tenant**:

| user_id | email | stored role | tenant |
|---|---|---|---|
| `u-admin-001` | `admin@myveticare.com` | `platform_admin` | none |
| `u-vet-001` | `vet@myveticare.com` | `veterinarian` | none |
| `u-owner-001` | `owner@myveticare.com` | `owner` | none |

The migration rehearsal, re-run live against this commit:

```
IDENTITY_SOURCE_COUNT=3   MIGRATABLE=0   QUARANTINED=3 (UNRESOLVED_NO_TENANT)
```

### The missing authority

```
PRE1_EXISTING_AUTHORITY_FOUND=NO
```

Searched and found empty: no tenant registry or catalogue exists in any of the 37
migrations; `tenant_id` is an unconstrained `TEXT` column with no foreign key and
no referenced table; no governance, authority or planning artefact names a
tenant; no artefact records these three identities.

The only tenant-shaped identifiers in the estate — `tenant_jeddah_001`,
`tenant_riyadh_001` — exist **only inside EP-05/EP-06 test fixtures**. They are
not offered as options: promoting a value whose authority is a file under
`tests/` would afterwards be indistinguishable from one the Sponsor chose.

**There is no tenant for these identities to be assigned to.**

### A fact the decision must answer

The seeded password `PetCare2026!` is a tracked literal at
`petcare_api/main.py:106,108,110`, in a repository whose visibility is **PUBLIC**.
Migrating these identities would create production accounts — one of them
`platform_admin` — whose password is published. Choosing a tenant does not
change that.

### Options

| | Option | Consequence |
|---|---|---|
| **1-A** | Sponsor names a tenant for each identity | they become migratable; the published credential must be rotated in the same act, or three production accounts ship with a known password |
| **1-B** | **Discard as seed artefacts — do not migrate** | nothing migrates; production identity is created through the governed invite-gated registration path; the public credential never reaches a durable store |
| **1-C** | Define a tenant registry first, then assign | PRE-1 re-opens after the registry exists; a tenant becomes a governed object rather than a free-text string |

**Option 1-B is the one repository evidence supports**: the source calls them
seed/test users, their password is public, no governance record treats them as
production identities, and there is no tenant for them to hold. 1-C is
recommended *in addition*, as follow-on work — the absence of a tenant registry
is a structural gap that outlives this decision.

`☐ 1-A   ☐ 1-B   ☐ 1-C   ☐ other: ______`

---

## SECTION 2 — PRE-2 / CONF-01 · role authority

### Three vocabularies, and the live consequence

| | Vocabulary | Where it lives |
|---|---|---|
| **V-A** | `Owner`, `Veterinarian`, `Platform Admin`, `Partner Clinic Admin` | `access_control.py`; the only set `require_role()` accepts; 9 backend guards |
| **V-B** | `owner`, `veterinarian`, `platform_admin`, `partner_clinic_admin` | minted by `seed_user` and registration; carried in the session and the `petcare_role` cookie |
| **V-C** | `owner`, `vet`, `pharmacy`, `admin` | `petcare_web/middleware.ts`, which **aliases V-B into V-C** |

> **Every identity this system creates is refused by every protected backend
> route with `403 Unknown role`.** The serving layer mints V-B; `require_role`
> accepts only V-A.

The suite does not show this because tests that need a working session seed the
V-A spelling directly — a value no production path produces.

### Which has more of the estate behind it

V-B is minted by the serving layer, carried in the session and the cookie,
submitted by `/register`, and is what `middleware.ts` is written to alias. V-A is
used by the nine route guards, and `strings.ts` already localises the display
names into Arabic and English — which is what display names are for.

No ratified artefact selects either. W0-D governs the *retired* role and is
silent on spelling.

### Options

| | Option | Migration impact | Privilege risk |
|---|---|---|---|
| **2-A** | Canonical **machine** roles (V-B) | none — stored values already are V-B; the `role` CHECK narrows from 8 spellings to 4 | expansion: low, same four concepts · denial: only test fixtures affected |
| **2-B** | Canonical **display** roles (V-A) | rewrite `user_identity.role` for every row; map `register`; rebuild the web role map | a mapping error during the rewrite is a silent promotion — the failure MIG-03 exists to catch |
| **2-C** | Machine role **IDs** as authority + display **labels** separate | as 2-A, plus labels stay in `strings.ts` where they already are | as 2-A |

**Recommendation: 2-C, with 2-A as its first step.** They are the same change to
authority; 2-C additionally stops display names from ever being authority
candidates. The estate already behaves this way everywhere except the nine route
guards, and a token that must be translated into Arabic cannot also be the token
authorization compares.

`☐ 2-A   ☐ 2-B   ☐ 2-C   ☐ other: ______`

### 2-D · a third item this ruling should also dispose of

The web still ships a **`pharmacy` role**: an alias, a protected `/pharmacy`
route, an `/account` allow-list entry, a full surface
(`petcare_web/app/pharmacy/page.tsx` — validated prescriptions, safety checks,
cold chain, dispense log), an onboarding page, and a home-page call to action.

W0-D requires the retired role to exist in no environment, and the backend
enforces that. The guard does not see the web because its needle is
`pharmacy_operator` and the web's short form is `pharmacy` — a literal mismatch,
not a scan-coverage gap. The guard is correct about the string it looks for.

Not fixed here: widening the needle would fail the build on legitimate clinical
vocabulary, since dispensing is a real veterinarian function with its own routes
and T-DISP controls. Separating "pharmacy the domain" from "pharmacy the role"
is a governed judgement, and removing a product surface is a product act.

`☐ remove the pharmacy role surface   ☐ retain it and record the exception   ☐ defer to a named lane`

---

## SECTION 3 — effect of the decision

### After PRE-1

| Ruling | Next action | Expected rehearsal result |
|---|---|---|
| 1-A | supply the Sponsor tenant map; re-run the rehearsal | `MIGRATABLE=3, QUARANTINED=0` |
| 1-B | mark the seeds non-migratable; identity is created through registration | `MIGRATABLE=0, QUARANTINED=0` — an empty, correct migration |
| 1-C | a tenant registry becomes a W-series requirement | unchanged until it exists |

### After PRE-2

| Ruling | Expected authorization behaviour |
|---|---|
| 2-A / 2-C | seeded and registered identities reach their permitted routes; `403 Unknown role` stops occurring |
| 2-B | the same outcome after a data rewrite that MIG-03 must police |

Under every combination the `user_identity.role` CHECK narrows from eight
spellings to four — a migration, and `GATE_LIVE_APPLY` once a database exists.

### What remains gated regardless

```
GATE_LIVE_APPLY            provision the database · apply the schema · apply the identity migration
GATE_CREDENTIAL_ENTRY      create the session signing secret
GATE_IRREVERSIBLE_ACTION   decommission the in-memory seeding
NEXT_GENUINE_GATE_AFTER_THIS_RULING=GATE_LIVE_APPLY (P1 — provision the database)
```

### What is NOT waiting on this ruling

W0-G's audit persistence is complete and merged as non-production engineering. It
required no approval and did not wait for one.

---

## Ruling

```
STATUS=RATIFIED
RULING_DATE=2026-09-12
RATIFIED_BY=[SPONSOR]  RATIFICATION_RECORD=RATIFICATION-001.md
AUTHORIZES_LIVE_APPLY=NO
AUTHORIZES_SECRET_CREATION=NO
AUTHORIZES_CUTOVER=NO
AUTHORIZES_IRREVERSIBLE_ACTION=NO
```

```
PRE1_RULING=1-B
  Discard the three seed identities. They are development artefacts, they do not
  migrate, and their published password must never become a production
  credential.

PRE2_RULING=2-C
  Machine role IDs are the sole authorization authority; display and localized
  labels are presentation only. The authority tokens are:
      platform_admin · partner_clinic_admin · veterinarian · owner

PHARMACY_ROLE=REMOVE
  `pharmacy` is not an authorization principal. No pharmacy-role authority is
  created or preserved.

PHARMACY_DOMAIN_CAPABILITIES=RETAIN_PENDING_ROLE_REBINDING
  Legitimate pharmacy and dispensing domain functionality remains, bound only to
  governed roles. Product capability is not deleted because the role was
  removed.

TENANT_REGISTRY_STATUS=REQUIRED_FOUNDATION
  Build the non-production constitutional and technical foundation for a tenant
  registry. Create no production tenant record and no production tenant
  assignment.
```

### Provenance — recorded precisely, because it matters

> **SUPERSEDED 2026-09-12 by `RATIFICATION-001.md`.** The block below is the
> record as it stood when the implementation was carried out, and it is left
> unedited. The rulings have since been given in the Sponsor's own voice with a
> `[SPONSOR]` tag; `RULING_ACTOR_TAG` is now `[SPONSOR]`, and PRE-1 and PRE-2 are
> ratified rather than implemented-on-instruction.
>
> The original text is preserved because a provenance record that is rewritten
> once the gap closes cannot later show that the gap existed.

```
RULING_CHANNEL=direct instruction to the execution lane, 2026-09-12
RULING_ACTOR_TAG=UNTAGGED          [SUPERSEDED — see RATIFICATION-001.md]
```

The rulings were given in the requester's own voice, in the session that
commissioned this lane, as a direct instruction to implement them — not relayed,
and not a claim about a decision taken elsewhere. They were framed as the
premises the implementation command assumes ("it assumes the Sponsor rulings now
are…") and carried no `[SPONSOR]` actor tag.

This is recorded rather than treated as an obstacle. The portfolio boundary's
concern is a **relayed, untagged block asserting a prior owner decision**; that is
not this. But an implementation of an authority-changing ruling should say on
what basis it proceeded, so that a reviewer can confirm the basis rather than
infer it. If the tag matters for the register, it is added here, not
reconstructed later.

Nothing in this document approves anything on the Sponsor's behalf: the ruling
above is a transcription of an instruction, and the recommendations that preceded
it are unchanged.

### What was NOT ruled

```
PRE2D_PHARMACY_SURFACE_DISPOSITION=NOT_RULED
```

The third checkbox — whether to remove the pharmacy product surface, retain it
with a recorded exception, or defer it to a named lane — was not answered.
`PHARMACY_DOMAIN_CAPABILITIES=RETAIN_PENDING_ROLE_REBINDING` answers the
capability question and leaves the surface's long-term disposition open. It is
carried forward as an open Sponsor decision.
