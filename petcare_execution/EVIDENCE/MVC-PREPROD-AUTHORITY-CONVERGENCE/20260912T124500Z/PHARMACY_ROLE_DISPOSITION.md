# PHARMACY_ROLE=REMOVE · PHARMACY_DOMAIN_CAPABILITIES=RETAIN_PENDING_ROLE_REBINDING

```
PHARMACY_ROLE_PRESENT=NO
PHARMACY_OPERATOR_PRESENT=NO   (as an authorization principal)
PHARMACY_DOMAIN_CAPABILITIES=REBOUND_OR_EXPLICITLY_NON_AUTHORITATIVE
```

## A7 — the inventory, classified

| Occurrence | Classification | Disposition |
|---|---|---|
| `middleware.ts` `ROLE_ALIAS.pharmacy` | AUTHORIZATION_ROLE | **removed** |
| `middleware.ts` `'/pharmacy': ['pharmacy','admin']` | AUTHORIZATION_ROLE (in the allowlist) | **rebound** to `['vet','admin']` |
| `middleware.ts` `'/account': [... 'pharmacy' ...]` | AUTHORIZATION_ROLE | **removed** |
| `middleware.ts` `'/pharmacy/:path*'` matcher | ROUTE PATH | retained |
| `app/pharmacy/page.tsx` | DOMAIN_CAPABILITY | retained |
| `app/onboarding/pharmacy/page.tsx` | DOMAIN_CAPABILITY | retained |
| `app/page.tsx` pharmacy CTA | UI_LABEL | retained |
| `lib/strings.ts` pharmacy strings | UI_LABEL | retained |
| `access_control.ROLE_PHARMACY_OPERATOR` | dead constant in the domain package | **registered pending** |
| `ai_hitl/service.py` `CONTEXT_ROLE_MAP` | reviewer routing, not authorization | **registered pending** |
| backend `VALID_ROLES` | never contained it | unchanged |

Nothing was deleted by grep. The ruling removes the PRINCIPAL and explicitly
retains the capability.

## A9 — why `/pharmacy` is bound to the veterinarian

Not a guess, and not a silent grant. The backend already proves who may perform
the underlying act: **dispensing requires `VETERINARIAN`**, asserted by
`T-DISP-01` as a positive control and by `T-DISP-03`/`T-DISP-04` as negative
ones. The page's dispensing region therefore has a governed actor, and the route
is bound to it.

The page's other regions — safety checks, cold chain — have no governed backend
action behind them at all. They are reachable but non-authoritative, and are
recorded as `DOMAIN_CAPABILITY_PENDING_ROLE_BINDING` rather than granted to
anyone by this change. No `pharmacist` or `pharmacy` role was invented to hold
them.

`partner_clinic_admin` is mapped to its own `clinic` category and reaches
`/account` only. No backend route names it, so giving it a privileged UI category
would show surfaces the API refuses.

## A10 — the guard that would have caught this

`tests/governance/test_retired_role_family.py`. The existing guard scans for one
literal, `pharmacy_operator`, and was correct about it — the web carried the
**short form**, and `"pharmacy_operator" not in "pharmacy"`.

Widening that needle would have been the wrong repair: dispensing is real
clinical vocabulary, and a guard that banned the word would fail the build on the
product the ruling retains. So the new guard is **context-aware** — it flags a
pharmacy-family term used as an authorization principal and ignores the same word
as a domain term, a page title, a route path or a business capability.

It tracks enclosing blocks, because the entry that actually shipped the defect was
`'/account': ['owner','vet','pharmacy','admin'],` — a line naming no role keyword
at all, three lines inside `protectedRoutes`. A line-by-line guard would have
missed the exact thing it exists for.

Nine meta-tests plant each required case:

```
pharmacy in an authorization allowlist   -> DETECTED
pharmacy as a role alias                 -> DETECTED
role == "pharmacy" in Python             -> DETECTED
the retired long form as a role          -> DETECTED
a session role of pharmacy               -> DETECTED
a pharmacy UI label                      -> NOT flagged
a pharmacy domain function               -> NOT flagged
'/pharmacy' as a retained route path     -> NOT flagged
the matcher listing the route            -> NOT flagged
```

## Registered pending, not excluded

Two occurrences live in `petcare_runtime`, a package the serving layer never
authorizes against. They are registered with reasons and line numbers rather than
excluded by tree, so a NEW occurrence still fails, and a register entry that stops
matching is itself a failure:

- `access_control.py:9` — `ROLE_PHARMACY_OPERATOR` is a **dead constant**.
  Nothing imports it and no `authorize_*` function compares against it. It is also
  the value `role_probes` derives the refused role from, so removing it would take
  away the only non-naming way tests can reach one.
- `ai_hitl/service.py:25` — a human-in-the-loop **reviewer routing** map. The key
  `pharmacy` is a review context; the value `pharmacist` names an eligible
  reviewer class with no authorization principal behind it. It decides who is
  asked to review, not who may act.

```
TESTS=tests/governance/test_retired_role_family.py   14 passed
      petcare_api/tests/test_role_authority.py (PHARM-ROLE-01..04)
```
