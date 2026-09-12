# A1 — every stateful surface in the serving path, classified

Scope of the sweep: `petcare_api/` (the serving process) and the module-level
state it constructs. Each surface is classified once, and a `PERSIST_NOW`
classification states WHICH governed requirement it satisfies — "it is in
memory" is not a reason to move something.

## PERSIST_NOW — moved in this change

| Surface | Was | Requirement it satisfies |
|---|---|---|
| `routers/auth.py::SESSION_STORE` | `InMemorySessionStore` | **AC-7.** Revocation across instances and across restarts. A session revoked in one process's memory stays live in another's, so the claim "sessions are revocable" is false the moment there is more than one instance. |
| `routers/auth.py::_users` | `dict[str, dict]` | **W0-F item 4 / W0-J.** Identity must survive the process, and W0-J's rehash-on-next-login is *lost* without it — the upgraded hash was discarded at every restart, so the credential migration never completed for anyone. |
| `routers/auth.py::_invite_codes` | `dict[str, dict]` | **Authorization, not durability.** Re-seeded at every start, so a consumed pilot code became unconsumed on restart and registration re-opened on a code that was already spent. |

## PERSIST_NOW — required, and deliberately NOT moved here

| Surface | Why not in this change |
|---|---|
| `main.py::_audit_log` | W0-G owns audit durability and migration `0028_w0g_audit_chain_columns.sql` already exists for it. Writing a second audit path here would create two writers for one chain, and a chain with two writers cannot establish ordering. `main.py::_audit_chain_persisted()` already reports `False` honestly rather than claiming durability it does not have. Remains `READY_PENDING_PRODUCTION_GATE`. |

## PERSIST_NOW — outside W0-F's boundary, recorded so the omission is deliberate

`main.py` holds four further dictionaries — `_sessions` (consultation sessions),
`_notes`, `_appointments`, `_prescriptions` — and the migration chain already
defines `clinical_note`, `pet`, `consent_record` and `uphr_document` for the same
concepts. The serving API is a pilot facade over tables the runtime defines and
the API does not use.

That is a real gap and it is **not** W0-F's. W0-F's boundary is identity,
tenancy, session and secret authority; the clinical domain has its own
requirements, its own migrations and its own acceptance criteria. Moving it here
would mean writing clinical persistence with no clinical acceptance criteria
attached to it, which is how a second divergent implementation starts.

Recorded as: `CLINICAL_SERVING_PERSISTENCE=GAP_OUTSIDE_W0F`.

## REMAIN_EPHEMERAL_BY_DESIGN

| Surface | Why |
|---|---|
| `secret_provider` client handles | An AWS client is a connection, not state. Caching one per process is correct; persisting one is meaningless. |
| `persistence.Persistence` | A holder for the constructed adapters. Rebuilt at start by construction. |

## Already durable — no change

| Surface | Backing |
|---|---|
| `main.py::consent_repo` | `ConsentRepository` writes JSON atomically (`tmp` then replace) to `CONSENT_STORE_PATH`. File-backed, not in-process. |
| `main.py::uphr_service` | `UPHRService` holds a cache over a `FileBackedRepository` and saves on every write. |

Both are file-backed rather than relational, which is a portability question for
the KSA move — a file on a host does not travel with a logical database dump.
Recorded, not changed: `FILE_BACKED_STATE=CONSENT_STORE,UPHR_STORE`.

## TEST_ONLY

`petcare_api/tests/pg_harness.py` — the ephemeral cluster and its databases.
Local loopback, temporary directory, removed at exit.
