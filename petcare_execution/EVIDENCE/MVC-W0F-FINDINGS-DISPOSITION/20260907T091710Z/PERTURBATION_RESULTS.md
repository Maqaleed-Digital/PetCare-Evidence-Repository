# Perturbation results — every new guard armed

No guard counts as proven because it passes. Each was made to fail by a single
controlled violation, then restored byte-for-byte and re-run.

## F1 — GCP legacy custody (`test_gcp_legacy_custody.py`)

| # | Violation | Result | Restored |
|---|---|---|---|
| P1 | active surface (`.github/workflows/verify.yml`) references `petcare_api/cloudbuild.yaml` | **FAIL** — `test_no_active_deployment_surface_references_a_retained_gcp_artefact` | clean |
| P2 | active surface invokes `gcloud builds submit` | **FAIL** — `test_no_active_deployment_surface_invokes_gcloud` | clean |

Baseline and restored: 5 passed.

## F2 — tree-wide retired-role absence (`test_retired_role_absence.py`)

Each live tree class perturbed separately, as required — a single probe in one
tree would not prove the others are scanned.

| # | Violation | Result | Restored |
|---|---|---|---|
| P1 | `pharmacy_operator` inserted into `petcare_api/main.py` | **FAIL** — `test_retired_role_absent_from_every_live_source_tree` | clean |
| P2 | inserted into `petcare_runtime/src/petcare/auth/access_control.py` | **FAIL** — same | clean |
| P3 | inserted into `scripts/governance/cross_repository_traceability.py` | **FAIL** — same | clean |

P2's worktree check reports a diff because that file carries the intentional
dead-field removal; the probe line itself was verified absent
(`grep -c 'perturbation probe'` → 0) and the remaining diff is exactly the two
deleted field declarations.

## F3 — in-file stale marker

| # | Violation | Result | Restored |
|---|---|---|---|
| P4 | `DO_NOT_IMPLEMENT_FROM_THIS_FILE` stripped from `policy_enforcer.ts` | **FAIL** — `test_artefacts_claiming_an_in_file_marker_actually_carry_one` | clean |

Baseline and restored: 5 passed.

```
PERTURBATION_GUARDS_PROVEN=6 (F1 ×2, F2 ×3, F3 ×1)
WORKTREE_RESTORED=YES — no perturbation committed
```
