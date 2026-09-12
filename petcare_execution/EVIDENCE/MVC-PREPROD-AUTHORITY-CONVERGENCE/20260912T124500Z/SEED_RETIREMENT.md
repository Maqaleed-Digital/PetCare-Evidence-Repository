# PRE-1 (1-B) — the seed identities, discarded

```
PRE1_RULING=1-B
PRE1_IMPLEMENTED=YES
SEED_IDENTITIES_FOUND=3
SEED_IDENTITIES_DISCARDED=3
SEED_RUNTIME_PATH_PRESENT=NO
PUBLISHED_SEED_PASSWORD_LIVE_PATH=NO
```

## What was removed

Three `seed_user(...)` calls at module scope in `petcare_api/main.py`, and with
them the password literal that appeared on lines 106, 108 and 110.

The reason is not tidiness. That password was a literal in a repository whose
visibility is PUBLIC, so **every start of a durable deployment would have written
three accounts with a published credential into the identity store, one of them
holding the highest role in the system**. W0-F's persistence is what would have
made it permanent: before persistence the accounts died with the process; after
it they would not have.

A startup path that creates a `platform_admin` from a source literal is a
backdoor whether or not anyone intended one.

## What was NOT removed

`seed_user` itself. Provisioning an identity programmatically is a legitimate
operator act; what was wrong was the CALLER at module scope. `SEED-05` asserts
the function still works by using it, deliberately, from a test.

The pilot invite codes are also still seeded at startup. They are outside this
ruling and are recorded as an observation, not changed — see
`OPEN_ITEMS` in `RUN_RECEIPT.md`.

## Controls

| ID | Control | Result |
|---|---|---|
| SEED-01 | importing the application in a FRESH process creates zero identities | PASS |
| SEED-01b | no module-level call to `seed_user` / `create_user` / `create_identity`, proven by AST over the serving tree | PASS |
| SEED-02 | the retired credential is absent from serving source **entirely**, comments included | PASS |
| SEED-02b | the retired identifiers are absent from serving **code** (a comment may record their removal) | PASS |
| SEED-02c | no credential-shaped literal anywhere in serving source | PASS |
| SEED-03 | `main.py` contains no `seed_user(` call at all — the fix is absence, not a skipped branch | PASS |
| SEED-04 | the migration rehearsal reports an EMPTY source, run in a fresh process | PASS |
| SEED-05 | fixtures are explicit and test-scoped | PASS |
| SEED-06 | no `platform_admin` from a published credential path; the retired credential no longer authenticates over the wire | PASS |

```
TESTS=petcare_api/tests/test_seed_retirement.py   16 passed
```

## Two things this work got wrong first, and how they were caught

**SEED-01 measured the suite, not the startup path.** `auth.IDENTITY_REPO` is
shared by the whole test run, so by the time the file executed, other modules had
legitimately provisioned their own fixtures and the count was not zero. The
question is what a DEPLOYMENT holds one second after boot, and only a clean
interpreter can answer it — the control now runs the import in a subprocess.

**SEED-02c could not see its own perturbation.** The matcher carried a negative
lookbehind, `(?<!_)`, intended to skip `password_hash`. It also skipped
`DEFAULT_ADMIN_PASSWORD` — and every credential-shaped name in the real world has
an underscore in front of the word. Found while designing the probe that was
supposed to make the control fail: the probe landed and the control passed. The
exclusion is now precise (`*_hash` only).
