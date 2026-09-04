# PORT-07..10 acceptance — every figure produced by running the suite

**Run:** 2026-09-04 · **Branch:** `govern/canonical-repository-authority`

| Suite | Command | Result |
|---|---|---|
| canonical python | `pytest tests/` | **73 passed** |
| — of which governance | `pytest tests/governance` | **39 passed** |
| runtime | `pytest petcare_runtime/tests` | **234 passed** |
| api | `pytest petcare_api/tests` | **46 passed** |
| web unit | `npx vitest run` | **120 passed** (18 files) |
| web types | `npx tsc --noEmit` | **clean** |
| web e2e | `npx playwright test` | **90 passed / 90** |

Playwright was run three times — baseline, after PORT-08, after PORT-09 — and
returned 90/90 each time. The responsive closure holds under every change in
this run.

## Deltas

| | Before | After |
|---|---|---|
| `tests/` | 10 collection errors | 73 passed |
| governance cases | 0 | 39 |
| vitest | 85 | 120 |
| ports DONE | 6 / 10 | **10 / 10** |

`tests/` previously failed collection entirely with
`ModuleNotFoundError: No module named 'petcare'` unless the operator exported
`PYTHONPATH`. A root `conftest.py` makes the path a property of the repository.

## Scans

```
ACTIVE_LITERAL_DEFAULT_IN_WORKING_TREE = 0
  (5 textual occurrences remain: 1 docstring, 1 rejection guard, 3 test constants)
SECRET_SCAN_OVER_THIS_RUN_COMMITS      = CLEAN
```

The substring grep `os.getenv("SECRET_KEY", "` reports 2 hits and both are
docstrings quoting the retired expression. The precise instrument — a
module-level `SECRET_KEY = os.getenv("SECRET_KEY", ...)` assignment — reports 0.
