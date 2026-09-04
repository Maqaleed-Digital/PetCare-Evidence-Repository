# MVC-W0F-ENGINEERING-HANDOFF-001 — serving-layer replacement

**Status:** `W0_F_AGENT_IMPLEMENTATION=NO` · `W0_F_ENGINEERING_HANDOFF=READY`
**Authority:** MVC-GOV-CANON-001. Standing instruction: *"STOP agent
implementation before large W0-F serving-layer replacement and prepare
`MVC-W0F-ENGINEERING-HANDOFF-001` for engineering-team implementation."*

This document exists so the work can be picked up by an engineering team. **No
agent lane may implement it.** Wave-0 A–E are complete and this is what remains.

## What W0-F is

`petcare_api` currently holds identity in process memory:

```python
# petcare_api/routers/auth.py
_users: dict[str, dict] = {}          # seeded at startup
_invite_codes: dict[str, dict] = {}   # seeded at startup
```

Every user, role, tenant assignment and invite code lives in a dict that dies
with the process and is not shared between instances. W0-C notes the consequence
directly: *"Persisting this per-user assignment is completed by W0-F."*

W0-F replaces that store with a persistent, governed serving layer. It is not a
refactor — it changes where identity lives, and identity is what four other
Wave-0 controls are anchored to.

## Why it is not agent work

Three properties put it outside an agent lane:

1. **It is the substrate for every security control in Wave-0.** A subtle error
   does not fail a test, it silently widens authorization.
2. **It requires a production data decision** — which store, in which region,
   under which residency authority. Residency is unresolved (`D.21 OPEN`).
3. **It requires migration of live identity**, which is irreversible.

## Security invariants that must survive — non-negotiable

| ID | Invariant | Where it lives now |
|---|---|---|
| **W0-A** | Session signing key comes from governed secret storage. Process refuses to start when unset, blank, or the retired literal. No default, ever. | `_require_secret_key()` |
| **W0-B** | Authorization derives from the **validated session**, never from a client header. | session-bound authz |
| **W0-C** | Tenant scope derives from the **identity**, established server-side. Client-supplied tenant values are selectors, never grants. | `seed_user(tenant_id=…)` |
| **W0-D** | Dispensing **fails closed to the veterinarian**. `pharmacy_operator` is retired and must not return. | fail-closed dispensing |
| **W0-E** | The service does not assert governance controls it cannot compute. | attestation surface |

**The A-before-B ordering is binding and must not be reversed.** Binding
authorization to a session signed with a publicly-known key replaces a header
bypass with a forgery bypass — strictly worse, because forged sessions look
legitimate. `test_w0_ab_ordering_invariant.py` enforces this and must stay green
throughout.

## Current session model — and its one favourable property

```
mechanism      stateless signed cookie (itsdangerous URLSafeTimedSerializer)
TTL            28800s (8h), enforced server-side at loads(max_age=…)
store          NONE — sessions are not persisted anywhere
revocation     NONE — no jti, no deny-list, no logout invalidation
key handling   single key, no previous-key acceptance list
```

Because there is one key and no fallback list, **rotating the key invalidates
every existing session**. If W0-F introduces a server-side session store or a
previous-key list, that property is lost and an explicit revocation path becomes
mandatory. Whichever way it goes, it must be a decision, not a side effect.

## Dependencies

- **Secret source** — AWS Secrets Manager vs SSM Parameter Store is deferred to
  the MyVetiCare AWS architecture decision. `_require_secret_key()` is
  deliberately indifferent to which supplies the environment.
- **Cloud authority** — AWS. GCP is `RETIRED_HISTORICAL`; do not target it.
- **Migrations** — 32 SQL migrations exist under `petcare_runtime/migrations/`.
  The canonical repository uses real migrations; the port source uses SQLAlchemy
  `create_all`. **Do not carry `create_all` across.**
- **Residency** — `D.21` is OPEN. Store placement cannot be finalised before it.

## Migration constraints

- Identity migration is **irreversible**; it needs a rehearsed rollback and a
  restore test, not just a backup.
- Password hashing today is bare `hashlib.sha256` with no salt and no KDF
  (`_hash_password`). **Do not migrate this forward.** W0-F is the correct point
  to move to a memory-hard KDF, and it must be treated as a credential migration
  with a rehash-on-next-login path, not a silent copy.
- Invite codes carry `expires_at` and must retain expiry semantics.

## Test estate that must stay green

```
petcare_api/tests/    46 tests, including
  test_secret_key_required.py        W0-A, 5 guards incl. an AST check
  test_w0_ab_ordering_invariant.py   the A-before-B invariant
  test_session_bound_authorization.py W0-B
  test_tenant_authority.py           W0-C
  test_dispensing_fail_closed.py     W0-D
  test_governance_attestation.py     W0-E
petcare_web/          85 vitest + 90 Playwright
```

Guards must remain **armed**: reintroducing a forbidden state must fail a test.
Verified for W0-A (3 failures on perturbation) and PORT-01/02 (2 failures).

## Marketplace preservation

The canonical marketplace domain is `petcare_runtime/src/petcare/partner_network/`
— **37 modules, EP-07 sealed**. W0-F must **consume, never re-own** it. Any
serving layer that reimplements catalogue, contracts or pricing duplicates a
sealed domain. Marketplace stays **not activated**.

## Arabic / RTL requirements

Arabic is the default language and RTL the default direction (FR-09). Any new
serving-layer surface inherits this. String literals go through `lib/strings.ts`;
absence guards (PORT-02) fail on untranslated Arabic slots and on JSX literals
the language toggle cannot reach.

## Acceptance criteria

1. All 46 `petcare_api` tests green, with guards proven armed by perturbation.
2. `petcare_web` 85 vitest + 90 Playwright green; `ASSERTIONS_WEAKENED=0`.
3. No `pharmacy_operator` anywhere in the tree.
4. Identity persists across process restart **and** across instances.
5. Tenant assignment is server-side and survives migration.
6. `SECRET_KEY` sourced from governed storage; startup fails closed without it.
7. Session revocation behaviour explicitly decided and documented.
8. Password storage uses a memory-hard KDF; no bare SHA-256 survives.
9. Rollback rehearsed against a restore, not merely planned.
10. Marketplace domain consumed, not duplicated; activation still fenced.

## Production gates

Every one of these is Sponsor-gated and none is agent work:
`GATE_LIVE_APPLY` (deployment, migration), `GATE_CREDENTIAL_ENTRY` (secret
storage), `GATE_IRREVERSIBLE_ACTION` (identity migration).

## Requirement authority

The product denominator is **499**, not the 106-row Implementation-B register.
W0-F acceptance traces against the 499 estate. `DENOMINATOR_STATUS=RELAYED_NOT_REMEASURED`.
