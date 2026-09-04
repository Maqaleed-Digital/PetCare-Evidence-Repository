# Manifest custody validation — re-run 2026-09-04

```
MANIFEST_DECLARED_FILES   = 315
MANIFEST_TRACKED_FILES    = 169
MANIFEST_UNVERSIONED      = 146
PIN                       = 146  ->  HOLDS
```

## The 146, by category

| Category | Count |
|---|---:|
| `.bak` | 15 |
| `__pycache__` | 57 |
| `baseline_input` | 74 |

Total 146. `OTHER` is 0 — every unversioned
citation is build output or a working-copy backup, none is an evidence artefact.

## No governed evidence claim depends on untracked material

```
CUSTODY_CITED_PATHS                  = 14
CUSTODY_CITED_UNTRACKED              = 0
MANIFEST_UNTRACKED_INTERSECT_CUSTODY = 0
```

The intersection is empty. `GATE_EVIDENCE_UNVERSIONED` closed the custody
question for the 14 cited evidence paths, and this confirms the manifest's
unversioned entries do not reopen it. They are noise in a dated snapshot,
not evidence protected by one working copy.

## Not remediated, deliberately

The manifest is a 2026-03-14 snapshot. Regenerating it over tracked files
only would change a dated artefact's bytes to make a test pass, which is
the failure mode the pin exists to prevent. The count is pinned at exactly
146 so that both a new unversioned citation and an accidental commit of
build output fail the guard.
