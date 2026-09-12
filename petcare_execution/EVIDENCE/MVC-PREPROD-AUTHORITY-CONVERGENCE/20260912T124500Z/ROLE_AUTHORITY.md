# PRE-2 (2-C) — machine role IDs are the sole authority

```
PRE2_RULING=2-C
PRE2_IMPLEMENTED=YES
CANONICAL_ROLE_IDS=platform_admin · partner_clinic_admin · veterinarian · owner
DISPLAY_ROLE_AUTHORITY_USAGE=0
```

## The single catalogue

`petcare_api/roles.py` holds the authority tokens and, separately, the display
labels. `main.py::VALID_ROLES` is now an **alias** of `ALLOWED_ROLES`, not a
second copy — two sets meant to be equal and drifting is precisely how CONF-01
happened.

| Surface | Before | After |
|---|---|---|
| `require_role()` / 9 route guards | display forms from `petcare.auth.access_control` | canonical machine ids |
| `user_identity.role` CHECK | 8 spellings (`0031`) | 4 canonical ids (`0033`) |
| `invite_code.allowed_role` | 8 spellings | 4 canonical ids |
| `app_session.role` | 8 spellings | 4 canonical ids |
| registration | machine ids (unchanged) | machine ids |
| session + `petcare_role` cookie | machine ids (unchanged) | machine ids |
| `petcare_web/middleware.ts` | aliased machine ids + legacy short forms | canonical ids → UI route categories |

## The domain package was NOT rewritten

`petcare.auth.access_control` keeps its own role tokens. They are that package's
vocabulary rather than display labels, it has 247 tests of its own, and the
serving layer never used its authorizer — `AccessContext`, `ResourceContext`,
`authorize_view_pet_profile` and `authorize_view_timeline` were imported by
`main.py` and never called. Switching the serving layer therefore changed no
domain authorization semantics.

## Controls

| ID | Control | Result |
|---|---|---|
| ROLE-01 | a canonical role is accepted on a permitted route | PASS |
| ROLE-02 | a canonical role is denied on a forbidden route — paired with the permitted role reaching the same route | PASS |
| ROLE-03 | a display label is not an authority token, cannot be stored, and is refused in a session | PASS |
| ROLE-04 | an unknown role is denied, and cannot be stored | PASS |
| ROLE-05 | comparison is exact | PASS |
| ROLE-06 | no case-folding or trimming promotes a value (`Platform_Admin`, ` platform_admin `, `admin`, `vet`) | PASS |
| ROLE-07 | the stored `role` CHECK holds only canonical ids, and no display label | PASS |
| ROLE-08 | the migration maps only canonical ids, identity-preserving | PASS |
| ROLE-09 | renaming a display label changes no authorization outcome | PASS |

```
TESTS=petcare_api/tests/test_role_authority.py   31 passed
```

## A security defect fixed on the way

`middleware.ts` resolved a role with `ROLE_ALIAS[rawRole] ?? rawRole`. An
**unmapped value passed straight through** — so a cookie carrying `admin`, a
value the serving layer has never minted, matched `['admin']` and opened the
admin surface. It is now `?? ''`: an unknown role has no category and is denied.

The legacy short forms (`admin`, `vet`, `owner`) and the dead `clinic_admin`
alias are gone with it.
