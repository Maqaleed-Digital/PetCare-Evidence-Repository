# `security/w0a-require-session-signing-key` — closure note (append-only)

```
HISTORICAL_W0A_BRANCH_CLASSIFIED = NON_DEPLOYABLE
```

## Findings

- The branch tip **predates W0-A2**.
- Its `petcare_api/routers/auth.py` and its historical test
  (`petcare_api/tests/test_secret_key_required.py`) both contained the
  **plaintext comparand** — implementation and its own test carrying the same
  literal.
- `filter-repo` therefore **necessarily redacted both**. This is the one ref in
  the published set where the rewrite touched a test file as well as the
  implementation.
- Consequently the rewritten historical tip is **not deployable**: its guard and
  its test were edited in step by a mechanical redaction, which is precisely the
  disarming signature the W0-A2 guard docstring names.

## What is unaffected

- **Rewritten `main` is unaffected.** Its head tree is byte-identical to the
  pre-purge tree (`MAIN_HEAD_TREE_IDENTITY.md`).
- `main` carries the **fingerprint-based W0-A2 guard**, which rejects the
  retired key at runtime by digest, holding no plaintext.

## Standing instruction

- This branch **must not be built, deployed, or merged again**.
- Its rewritten tip `a838d9f2b43e7cdcee659fab9729915533b78884` is retained as a
  historical record only.
- **Branch deletion is a separate future repository-cleanup act.** It was not
  performed in this run and is not authorized by this closeout.
