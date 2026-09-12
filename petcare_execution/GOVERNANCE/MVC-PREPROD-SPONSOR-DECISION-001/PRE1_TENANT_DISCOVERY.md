# PRE-1 — tenant assignment: what the repository actually contains

**No tenant is chosen in this document.** It reports what the estate holds, so
that the decision is made on evidence rather than on the shape of the question.

```
PRE1_SOURCE_COUNT=3
PRE1_MIGRATABLE_BEFORE_DECISION=0
PRE1_QUARANTINED=3          all UNRESOLVED_NO_TENANT
PRE1_EXISTING_AUTHORITY_FOUND=NO
PRE1_DECISION_REQUIRED=YES
```

Re-verified live at `77d921e` by running the dry-run, not carried from the prior
receipt.

---

## 1 · The three identities, verbatim from source

`petcare_api/main.py`, under the comment **"Seed pilot test users (in-memory — no
DB yet)"**:

| user_id | email | role (as stored) | tenant | full_name |
|---|---|---|---|---|
| `u-admin-001` | `admin@myveticare.com` | `platform_admin` | **none** | Platform Admin |
| `u-vet-001` | `vet@myveticare.com` | `veterinarian` | **none** | Dr. Test Vet |
| `u-owner-001` | `owner@myveticare.com` | `owner` | **none** | Test Owner |

`seed_user` is called without a `tenant_id` argument for all three, so the field
is absent rather than empty — the legitimate "no tenant assignment" state W0-C
defines, which fails closed at `require_tenant()` with `403 NO_TENANT_AUTHORITY`.

---

## 2 · The search for existing authority — and what it found

The instruction is to consume an existing authority rather than ask for a
decision already taken. The search was run and returned nothing, which is itself
the most important finding here.

| Searched | Result |
|---|---|
| a tenant registry or catalogue table in any of the 37 migrations | **none exists** |
| `tenant_id` column definitions | present on many tables as **unconstrained `TEXT NOT NULL`** — no foreign key, no `CHECK`, no referenced table |
| governance artefacts naming a tenant (`petcare_execution/GOVERNANCE`, `AUTHORITY`, `PLANNING`) | **no artefact names any tenant** |
| any record of these three identities in governance or evidence | **none** |
| tenant-like identifiers anywhere in the estate | `tenant_jeddah_001` (42×) and `tenant_riyadh_001` (1×) — **all of them inside EP-05/EP-06 test fixtures**, in `tests/ep05/` and `tests/ep06/` |

**There is no tenant to assign these identities to.** A tenant in this estate is
a free-text string that each caller supplies; nothing creates one, records one,
or constrains one. So PRE-1 is not only "which tenant" — it is prior to that:
whether a tenant exists, and how one comes into being.

```
TENANT_REGISTRY_EXISTS=NO
TENANT_IS_AN_UNCONSTRAINED_TEXT_FIELD=YES
```

Nothing was inferred from an email address, a role, a test name, a UI route, or a
prior assumption. `tenant_jeddah_001` is **not** proposed as an option: it appears
only in EP-05/EP-06 test fixtures and no governance record establishes it.

---

## 3 · A material fact the decision should not be made without

These three identities carry the password literal `PetCare2026!`, written into
`petcare_api/main.py` at lines 106–110 and **tracked in this repository, whose
visibility is PUBLIC** (`gh repo view` → `visibility=PUBLIC`).

Migrating them into a production identity store would create three production
accounts — one of them `platform_admin` — whose password is published.

This is not an argument for any particular option; it is a fact each option has
to answer. It also does not go away by choosing a tenant.

```
SEED_PASSWORD_IS_A_PUBLIC_LITERAL=YES  petcare_api/main.py:106,108,110
REPOSITORY_VISIBILITY=PUBLIC
```

---

## 4 · The decision

| identity | role | assignment required | permitted options | consequence |
|---|---|---|---|---|
| `u-admin-001` | `platform_admin` | a tenant, or a disposition | **(A)** assign a Sponsor-named tenant · **(B)** discard as seed artefact · **(C)** define a tenant registry first, then assign | A: a published credential becomes a production platform-admin account unless rotated at the same time · B: nothing migrates; production identity is created fresh · C: PRE-1 reopens after the registry exists |
| `u-vet-001` | `veterinarian` | same | same | same, at veterinarian scope |
| `u-owner-001` | `owner` | same | same | same, at owner scope |

### Option B is supported by repository evidence

Recorded because the instruction permits the discard option **only** where
evidence supports it. Four independent pieces do:

1. the source comment calls them *"Seed pilot test users (in-memory — no DB yet)"*;
2. their password is a public literal;
3. no governance or evidence artefact records them as production identities;
4. they hold no tenant, and no tenant exists for them to hold.

### What is NOT recommended

Assigning a tenant that appears only in a test fixture. That would take a value
whose authority is a `.py` file under `tests/` and make it a production scope —
and afterwards it would be indistinguishable from one the Sponsor chose.

---

## 5 · What happens after the ruling

| Ruling | Next action | Expected dry-run result |
|---|---|---|
| A — assign tenants | supply a tenant map; re-run the rehearsal | `MIGRATABLE=3, QUARANTINED=0` |
| B — discard | mark the seeds non-migratable; production identity is created through the governed registration path | `MIGRATABLE=0, QUARANTINED=0` (source empty) |
| C — registry first | a tenant registry becomes a W0-series requirement; PRE-1 re-opens | unchanged until then |

Under every option the production apply remains `GATE_LIVE_APPLY` +
`GATE_IRREVERSIBLE_ACTION`.
