# Fresh-clone verification

A **completely fresh** clone from `origin`, not the pre-rewrite working copy.

```
FRESH_CLONE_MAIN       = 3cef8f9db73a07aab33e953ac7d41c8b238d159d
FRESH_CLONE_MAIN_MATCH = YES
git cat-file -t 5202bb5f…  ->  fatal: could not get object info
```

Protection re-read from the fresh clone:

```
context=verify  app_id=15368  strict=true  admins=true  force=false  deletions=false
```

## Validation surface — the whole `verify` job, run locally

| step | result |
|---|---|
| `pytest tests petcare_runtime/tests petcare_api/tests` | **428 passed**, 0 failed |
| `tsc --noEmit` (typecheck) | **rc 0** |
| web unit tests (vitest) | **120 passed**, 18 files |
| responsive regression (Playwright, 7 viewports) | **90 passed** |
| prohibited-literal scan | `SCANNED=358 ACTIVE_LITERAL_DEFAULT=0` |
| secret scan | `SCANNED=3713 FINDINGS=0 SECRET_SCAN=CLEAN` |
| evidence bundle verification | `BUNDLES=10 ARTEFACTS=76 FAILED=0` |

```
FRESH_CLONE_TESTS       = 428 python + 120 web unit = 548 passed, 0 failed
RESPONSIVE              = 90 passed
SECRET_SCAN             = CLEAN
PROHIBITED_LITERAL_SCAN = CLEAN
```

Raw output: `FRESH_CLONE_PYTEST.txt`, `FRESH_CLONE_WEB.txt`,
`FRESH_CLONE_E2E.txt`, `FRESH_CLONE_SCANNERS.txt`.

## Two failures were found and both are accounted for

**1. PORT closing commits — a real defect, repaired.** See
`LINEAGE_CITATION_REMAP.md`. This was also failing in CI on `main`.

**2. `test_every_authority_source_path_resolves` (AUTH-11) — environmental, not
repaired.** This test is **skipped in CI** (`7 skipped`); it runs only when the
port-source repository is checked out locally. It failed because the AUTH-11
row in the *port-source* repository cites an **absolute path** into this
repository's working copy —
`/Users/waheebmahmoud/dev/petcare-evidence-repository/evidence/G-R1/`.

The `evidence/` tree exists at `origin/main` but **not** at `4f36096b…`, the
commit-map-mandated local `main`. Reconciling the local ref therefore removed
the directory that the absolute path points at, and the citation stopped
resolving. Fast-forwarding local `main` to `origin/main` restored it, after
which the full estate is **428 passed, 0 failed**.

No repository content was changed for this. It is a cross-repository authority
table depending on an absolute path into a second working copy — a real
brittleness, but not a Gate-5 defect and not in this closeout's scope. It is
recorded here rather than quietly fixed.
