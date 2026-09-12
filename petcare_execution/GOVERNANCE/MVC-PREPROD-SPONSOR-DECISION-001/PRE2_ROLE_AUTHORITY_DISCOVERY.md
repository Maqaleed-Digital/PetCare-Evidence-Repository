# PRE-2 / CONF-01 — role authority: what the repository actually contains

**No role is normalised in this document.** Nothing here changes authorization
behaviour.

```
CONF01_STATUS=OPEN
PRE2_EXISTING_AUTHORITY_FOUND=NO_RATIFIED_AUTHORITY
PRE2_DECISION_REQUIRED=YES
```

---

## 1 · There are THREE vocabularies, not two

The conflict was reported as two. Live source shows three, and the third is the
one that changes the recommendation.

### V-A · authorization vocabulary — display form

`petcare_runtime/src/petcare/auth/access_control.py`

```
ROLE_OWNER               = "Owner"
ROLE_VETERINARIAN        = "Veterinarian"
ROLE_PARTNER_CLINIC_ADMIN= "Partner Clinic Admin"
ROLE_PLATFORM_ADMIN      = "Platform Admin"
ROLE_PHARMACY_OPERATOR   = "Pharmacy Operator"   ← retired, excluded from VALID_ROLES
```

`main.py::VALID_ROLES` is exactly the first four, and `require_role()` accepts
**only** these. Nine backend route guards compare against them.

### V-B · serving vocabulary — machine form

`petcare_api/roles.py`, minted by `seed_user` and by invite-gated registration

```
owner · veterinarian · partner_clinic_admin · platform_admin
```

This is what goes into the session payload and into the `petcare_role` cookie.

### V-C · web middleware vocabulary — short form

`petcare_web/middleware.ts`

```
ROLE_ALIAS = { platform_admin: 'admin', clinic_admin: 'admin',
               veterinarian: 'vet', admin: 'admin', vet: 'vet',
               owner: 'owner', pharmacy: 'pharmacy' }
protectedRoutes = { '/owner': ['owner','admin'], '/vet': ['vet','admin'],
                    '/pharmacy': ['pharmacy','admin'], '/admin': ['admin'],
                    '/account': ['owner','vet','pharmacy','admin'] }
```

---

## 2 · The authority matrix

| Role literal | Origin | Created by | Persisted by | Recognised by `require_role` | Routes granted | Routes denied | UI expectation |
|---|---|---|---|---|---|---|---|
| `Owner` | `access_control.ROLE_OWNER` | nothing in the serving path | `user_identity.role` (catalogue admits it) | **YES** | appointments, timeline | vet-only routes | none — the web never emits it |
| `Veterinarian` | `access_control.ROLE_VETERINARIAN` | nothing | same | **YES** | consultations, notes, prescriptions, dispense | admin-only | none |
| `Platform Admin` | `access_control.ROLE_PLATFORM_ADMIN` | nothing | same | **YES** | all nine, incl. `/audit/events` | — | `strings.ts` uses it as a **display label** (ar: مدير المنصة) |
| `Partner Clinic Admin` | `access_control.ROLE_PARTNER_CLINIC_ADMIN` | nothing | same | **YES** | — (no route names it) | all | none |
| `owner` | `main.py::seed_user`, `register` | serving layer | `user_identity.role` | **NO** | **none** | **all nine** | `/register` option value; middleware `owner` |
| `veterinarian` | `main.py::seed_user`, `register` | serving layer | same | **NO** | **none** | **all nine** | `/register` option value; middleware aliases → `vet` |
| `platform_admin` | `main.py::seed_user` | serving layer | same | **NO** | **none** | **all nine** | middleware aliases → `admin` |
| `partner_clinic_admin` | `roles.py` catalogue | nothing | same | **NO** | none | all | none |
| `clinic_admin` | `middleware.ts` alias only | nothing | not storable | **NO** | — | — | dead alias — matches no vocabulary |
| `pharmacy` | `middleware.ts` alias + `protectedRoutes` | nothing | not storable | **NO** | `/pharmacy` in the web | — | a full `/pharmacy` surface exists |

### The behavioural consequence, stated plainly

The serving layer mints V-B. `require_role()` accepts only V-A. **Every identity
this system creates is refused by every protected backend route with
`403 Unknown role`.** The three seeded pilot identities sign in successfully and
can do nothing.

The suite does not show it because tests that need a working session seed the
V-A spelling directly (`auth.seed_user("u-x", "x", "pw", api.ROLE_OWNER, ...)`),
which no production path ever produces.

---

## 3 · Which vocabulary has more of the estate behind it

Evidence, not preference:

| | V-A (display) | V-B (machine) |
|---|---|---|
| minted by the serving layer | no | **yes** |
| carried in the session and the `petcare_role` cookie | no | **yes** |
| what `middleware.ts` is written to alias | no | **yes** (`platform_admin`, `veterinarian`) |
| what `/register` submits | no | **yes** |
| accepted by `require_role` | **yes** | no |
| used as a display label in `strings.ts` | **yes** (already localised ar/en) | no |

`strings.ts` already localises the display names, which means display form is an
i18n concern that exists independently. A vocabulary that must be translated for
Arabic cannot also be an authority token.

**No ratified governance artefact selects either.** W0-D governs the *retired*
role and says nothing about spelling. So the authority is genuinely unsettled.

---

## 4 · A third finding the decision has to cover

The web still ships a **`pharmacy` role**: an alias in `ROLE_ALIAS`, a protected
route `/pharmacy`, an entry in `/account`'s allow-list, a full surface at
`petcare_web/app/pharmacy/page.tsx` (validated prescriptions, safety checks, cold
chain, dispense log), an onboarding page, and a home-page call to action.

W0-D says the retired role "must not exist in any environment", and the backend
enforces that. The guard does not see the web, because:

```
retired-role needle = "pharmacy_operator"
web short form      = "pharmacy"          ← does not match
live_source_trees   includes petcare_web/app, petcare_web/lib, petcare_web/components
```

The guard scans those trees and reports zero occurrences, correctly, of a string
that is not the one in use.

**Not fixed here, deliberately.** Widening the needle to `pharmacy` would fail the
build on legitimate clinical vocabulary — dispensing is a real function that
veterinarians perform, and `petcare_api` has dispensing routes and T-DISP
controls for exactly that. Distinguishing "pharmacy the domain" from "pharmacy
the role" is a governed judgement, and removing a product surface is a product
act.

```
RETIRED_ROLE_SURVIVES_IN_WEB_AS_SHORT_FORM=YES
GUARD_BLIND_TO_IT=YES  (needle mismatch, not a scan-coverage gap)
```

---

## 5 · Options

### OPTION A — canonical machine roles (`platform_admin` / `veterinarian` / `owner` / `partner_clinic_admin`)

- **identities affected:** all 3 seeded; every future registration — none change value
- **routes affected:** all 9 backend guards change comparand; `require_role` accepts V-B
- **migration impact:** none — stored values already are V-B; `user_identity.role` CHECK narrows
- **compatibility:** `middleware.ts` already aliases V-B; `/register` already submits it; `strings.ts` keeps display names as labels
- **privilege-expansion risk:** low — the set is the same four concepts; no identity gains a route it could reach today (today it can reach none)
- **privilege-denial risk:** any identity currently storing a V-A spelling stops being recognised. Only test fixtures do that
- **evidence weight:** carries the serving layer, the cookie, the web middleware and the registration form

### OPTION B — canonical display roles (`Platform Admin` / `Veterinarian` / `Owner` / `Partner Clinic Admin`)

- **identities affected:** all 3 seeded must be rewritten; `register` must map its form value
- **routes affected:** none — the guards already use V-A
- **migration impact:** a data migration rewriting `user_identity.role` for every row, plus a `CHECK` change
- **compatibility:** `middleware.ts` aliases break (`platform_admin` no longer emitted; `"Platform Admin"` is not a key) — the web would need its own map
- **privilege-expansion risk:** a mapping error during the rewrite is a silent promotion — the failure MIG-03 exists to prevent
- **privilege-denial risk:** the `petcare_role` cookie changes shape; existing sessions stop matching the middleware
- **evidence weight:** carries the backend guards only

### OPTION C — machine role IDs as authority, display labels separate

- **identities affected:** as Option A
- **routes affected:** as Option A
- **migration impact:** as Option A, plus a label table or i18n key per role — `strings.ts` already holds the labels
- **compatibility:** highest; separates authority from presentation permanently
- **privilege-expansion risk:** as Option A
- **privilege-denial risk:** as Option A
- **evidence weight:** as Option A, and additionally consistent with `strings.ts` already localising display names

### Recommendation

**OPTION C**, with **OPTION A** as its first step — they are the same change to
authority, and C only adds that display names stop being candidates for
authority at all. Recommended because the estate already behaves this way
everywhere except the nine route guards, and because a token that must be
translated into Arabic cannot also be the token authorization compares.

**This is a recommendation, not a ruling.** No authority-changing implementation
is performed without the Sponsor's decision.

---

## 6 · What happens after the ruling

| Ruling | Implementation | Expected behaviour |
|---|---|---|
| A or C | change the nine guards' comparand and narrow the `user_identity.role` CHECK to one vocabulary | seeded and registered identities reach their routes; `403 Unknown role` stops |
| B | rewrite stored roles, map `register`, rebuild the web role map | same outcome, more moving parts, and a rewrite that MIG-03 must police |
| any | the `pharmacy` web surface still needs its own disposition | — |

Under every option the `user_identity.role` CHECK narrows from eight spellings to
four, which is a migration and is `GATE_LIVE_APPLY` once a database exists.
