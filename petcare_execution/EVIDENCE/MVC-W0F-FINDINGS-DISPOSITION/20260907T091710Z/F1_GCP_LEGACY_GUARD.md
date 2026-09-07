# F1 — GCP build configuration: custody, not deletion

**Finding.** Six GCP Cloud Build files remain in the tree while
`CURRENT_CLOUD_AUTHORITY=AWS`. No guard asserted anything about them.

**Disposition.** Retained under custody. Not deleted.

Deleting delivery configuration destroys the record of how the estate was
previously built, and that record is evidence. The governing distinction is
therefore not presence but use:

```
file existence     = permitted legacy custody
active reference   = forbidden
```

## The six, enumerated and classified

All `LEGACY_RETAINED_NOT_ACTIVE`:

| Path |
|---|
| `petcare_api/cloudbuild.yaml` |
| `petcare_web/cloudbuild.yaml` |
| `petcare_execution/PHASE_2/DF03/cloudbuild.nonprod.yaml` |
| `petcare_execution/PHASE_2/DF03/cloudbuild.prod.yaml` |
| `petcare_execution/PHASE_2/DF03B/cloudbuild.nonprod.smoke.yaml` |
| `petcare_execution/PHASE_2/DF04/cloudbuild.nonprod.app.yaml` |

Register: `GOVERNANCE/CANONICAL_REPOSITORY_AUTHORITY/GCP_LEGACY_CUSTODY_REGISTER.json`
(`MVC-GCP-LEGACY-CUSTODY-001`).

## What counts as an active deployment surface

A surface CI or a hosting provider actually executes. In this repository that set
is exactly four:

```
.github/workflows        GitHub Actions
render.yaml              Render service definition
petcare_api/Dockerfile   container build
petcare_web/Dockerfile   container build
```

Evidence quotations do not count as use: a governance document naming
`cloudbuild.yaml` while explaining why it is retired is doing its job. Only the
four surfaces above are scanned, so no exclusion list is needed for prose.

## Guard — `tests/governance/test_gcp_legacy_custody.py`

Five assertions:

1. the active-surface set is non-empty (the absence guards are not vacuous);
2. every registered artefact still exists (custody claims stay true);
3. every `cloudbuild*.y*ml` on disk is registered (no unregistered drift);
4. no active surface references a registered artefact;
5. no active surface invokes `gcloud`.

Assertions 3 and 5 are the ones that catch a *new* GCP dependency, not merely a
resurrected old one.

## Measured

```
GCP_LEGACY_FILES=6
GCP_ACTIVE_REFERENCES=0
GCP_GUARD_ARMED=YES
```
