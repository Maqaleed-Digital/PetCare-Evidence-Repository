# A17 — Rule 18 re-measure, from live source

Re-read after this lane's changes. Nothing inherited.

| | Status | Implementation | Serving path | Persistence | Tests |
|---|---|---|---|---|---|
| **W0-F** | `READY_PENDING_PRODUCTION_GATE` | secret provider, repositories, persistence mode | `auth.py` sign-in / register / read_session | `0031` + `0034` FK | 82 + 31 |
| **W0-G** | `READY_PENDING_PRODUCTION_GATE` | `audit_repository.py` | `main.py::_audit`, 11 call sites | `0028` + `0032` | 22 + 6 |
| **W0-H** | `READY_PENDING_PRODUCTION_GATE` | `0029` staged, `SET NOT NULL` with recorded precondition | none in `petcare_api` — commerce is `petcare_runtime` | additive, NULLable | 7 |
| **W0-J** | `READY_PENDING_PRODUCTION_GATE` | scrypt; persisted identity; durable rehash | sign-in / register | `0031` + `0033` | 48 |

```
W0F_STATUS=READY_PENDING_PRODUCTION_GATE
W0G_STATUS=READY_PENDING_PRODUCTION_GATE
W0H_STATUS=READY_PENDING_PRODUCTION_GATE
W0J_STATUS=READY_PENDING_PRODUCTION_GATE
```

None is `CLEAN`, and none is claimed to be — each still requires production
evidence that only a live apply can produce.

## W0-J's blocker is gone

The previous re-measure recorded `W0J = READY_PENDING_PRODUCTION_GATE + PRE-1`.
PRE-1 is ruled and implemented, so the qualifier is discharged: the migration is
empty by design rather than blocked on a decision.

## A18 — ARCH-01 is NOT closed

```
AUDIT_CHAIN_INTEGRITY=IMPLEMENTED
AUDIT_WRITE_AUTHORITY=SERVER_ESTABLISHED
SIGNATURE_ANCHORING=OPEN
```

Nothing in this lane touched it, and nothing here should be read as closing it.
A hash chain detects tampering by anyone without write access to the whole log;
it does not defend against an actor who can rewrite every row and recompute every
digest. `test_aud_09` asserts the limit directly: a forged event chains like any
other and the chain verifies — what stops it being authoritative is that its
identity fields are neutralised at the boundary, not that the chain rejected it.

**A valid hash chain is not write authenticity.** Whether signatures or external
anchoring are required against V3.2 §25/§26 remains a specification question.
