# Canonical vs Port-Source Differential, and the Port Plan

**Under:** `MVC-GOV-CANON-001`
**Date:** 2026-09-03 · **Statuses last reconciled:** 2026-09-04

> The status column of the port table and the exception table below are the prose
> half of a two-artefact register. The falsifiable half is `PORT_REGISTER.json`,
> and `tests/governance/test_canonical_register_integrity.py` fails if the two
> disagree — so neither can drift silently away from the other again.
**Canonical:** `petcare-evidence-repository` · **Port source:** `petcare-platform` (`LEGACY_TO_PORT_FROM`)

## The fact that shapes the whole plan

The two serving layers do not share a technology.

| | Canonical `petcare_web/` | Port source `petcare-platform/frontend/` |
|---|---|---|
| Framework | Next.js 14.2.25, App Router | CRA 5 + craco |
| Language | **TypeScript** (`.tsx`) | **JavaScript** (`.jsx`) — 0 TS sources |
| React | 18.3.1 | 19.2.3 |
| i18n | `LangProvider` + `t({ar, en})` inline | `react-i18next` + `locales/{ar,en}.json` |
| Tests | vitest + Testing Library (76) | Jest via craco (49) |
| E2E | Playwright **already present** (`e2e/pilot-path.spec.ts`) | Playwright added this lane (84 assertions) |
| Routing | file-system `app/` | `react-router-dom` + `ProtectedRoute` |

**Nothing ports as a file.** Every tranche below is a re-expression: the
*behaviour and the assertion* move, the code does not. A plan that assumed
copying would be wrong at the first import.

A second observation, recorded but not acted on: the canonical repository
contains **two** web trees, `petcare_web/` (68 tracked, Playwright + vitest) and
`petcare-web/` (79 tracked). Their relationship is not established by any
authority read in this lane. Recorded as `WEB_TREE_DUPLICATION_OPEN`. All port
targets below name `petcare_web/`, which is the tree carrying the test estate.

## Differential

| Capability | Classification | Note |
|---|---|---|
| Marketplace / partner network | `CANONICAL_ONLY` | EP-07 sealed, 37 modules. Never rebuild in the port source. |
| Financial execution, payment activation, integration control | `CANONICAL_ONLY` | EP-08…EP-12 closure branches |
| Intelligent ops, AI runtime/governance | `CANONICAL_ONLY` | AI_RUNTIME tree |
| SQL migrations | `CANONICAL_ONLY` | 34 migrations; port source uses SQLAlchemy create_all |
| Trust surfaces, PDPL rights, consent state, advisory disclosure | `CANONICAL_SUPERIOR` | WO-002 work, 14 test files |
| Invite-gated registration | `CANONICAL_SUPERIOR` | canonical has it with 8 tests; port source has no registration surface |
| Wave-0 identity hardening (session-derived authz, tenant scope from identity, fail-closed dispensing) | `CANONICAL_SUPERIOR` | on `wave0/…`, local-only, 8 commits ahead of main |
| **Error boundary** | `PORT_SOURCE_SUPERIOR` | **PORTED — PORT-03, done** |
| **Viewport/layout harness breadth** | `PORT_SOURCE_SUPERIOR` | canonical Playwright covers one pilot path; port source covers 10 routes x 7 viewports |
| **Absence-guard discipline** (assert the forbidden state, not just the good one) | `PORT_SOURCE_SUPERIOR` | proven-armed guards |
| **Governance register integrity tests** | `PORT_SOURCE_SUPERIOR` | `test_phase16_governance_integrity.py` |
| Role-journey navigation model | `EQUIVALENT` / `NOT_COMPARABLE` | canonical uses file-system routing; the port source's `journeys.js` model has no direct analogue |
| Arabic-first defaults | `EQUIVALENT` | both `lang=ar` / `dir=rtl` by default |
| Odoo / ZATCA boundary | `INTEGRATION_REQUIRED` | port source has adapter ports; canonical has EP-09/EP-10 |

## Port plan

| PORT_ID | Capability | Target | Risk | Status |
|---|---|---|---|---|
| **PORT-01** | Absence-guard discipline in canonical tests | `petcare_web/__tests__/absence-guards.test.ts` | low | **DONE** |
| **PORT-02** | Arabic absence guards (no hard-coded English on customer paths) | `petcare_web/__tests__/absence-guards.test.ts` | low | **DONE** |
| **PORT-03** | **Error boundaries** | `app/error.tsx`, `app/global-error.tsx` | low | **DONE** |
| **PORT-04** | Viewport breadth — 7 viewports x canonical routes | `petcare_web/e2e/viewport-invariants.spec.ts` | medium | **DONE** |
| **PORT-05** | Safety-critical 320 px reachability (emergency, pharmacy, consultation) | `petcare_web/e2e/viewport-invariants.spec.ts` | medium | **DONE** |
| **PORT-06** | Page-crash detection in e2e | `petcare_web/e2e/viewport-invariants.spec.ts` | low | **DONE** |
| **PORT-07** | Governance register integrity tests, retargeted to canonical authorities | `tests/governance/test_canonical_register_integrity.py` | medium | **DONE** |
| **PORT-08** | Empty / loading / error state coverage per surface | `petcare_web/__tests__/surface-states.test.tsx` | medium | **DONE** |
| **PORT-09** | Marketplace UI seam against canonical `partner_network` services | `petcare_web/lib/marketplace.ts`, `petcare_web/app/admin/` | medium | **DONE** — consumes, never re-owns; seam unwired because activation is not authorized |
| **PORT-10** | Cross-repository traceability denominator | `petcare_execution/GOVERNANCE/CANONICAL_REPOSITORY_AUTHORITY/CROSS_REPOSITORY_TRACEABILITY.md` | medium | **DONE** |

### Ordering constraint

PORT-04…PORT-06 extend the existing `petcare_web/playwright.config.ts` rather
than introducing a second harness. The port source's harness is a separate npm
package only because that repository has an unrelated peer-dependency conflict;
that reason does not exist here and must not be carried across.

### What must not be ported

The `pharmacy_operator` role. Canonical wave-0 (`W0-D`) **retires** it and fails
dispensing closed to the veterinarian. The port source still carries
`pharmacy_operator` as a first-class role across journeys, RBAC and fixtures.
Porting the port source's role model would reverse a security decision. Any
tranche touching roles must adopt the canonical model, not the port source's.

## Open exceptions

| ID | Status |
|---|---|
| `GATE_EVIDENCE_UNVERSIONED` | **CLOSED 2026-09-03** — `GATE_EVIDENCE_UNVERSIONED_CLOSURE.md`; 40 tracked, 14/14 cited paths hash-bound |
| `EPIC_IDENTIFIER_COLLISION` | EP-06 = Emergency Network (canonical) vs Security/Audit/Ops (port source) |
| `WEB_TREE_DUPLICATION_OPEN` | **CLOSED 2026-09-03** — `WEB_TREE_AUTHORITY_RECONCILIATION.md`; `petcare_web` canonical, `petcare-web` SUPERSEDED_PROTOTYPE |
| `CANONICAL_HEAD_LOCAL_ONLY` | **PARTIALLY CLOSED 2026-09-04** — W0-A reached `origin/main` via PR #3 (`0364fe69`). W0-B…W0-E remain local-only. |
