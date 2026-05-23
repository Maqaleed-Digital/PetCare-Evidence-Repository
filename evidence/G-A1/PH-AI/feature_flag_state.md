# PH-AI — AI Feature-Flag State Snapshot

Snapshot of what this evidence repository **can verify** about the AI
feature-flag state, and what it cannot. This document is part of the CLOSE 3
preparation pass — it does not re-verify runtime state, and it does not
assert that PH-AI is ready to activate.

## Snapshot

- **Snapshot date:** 2026-05-23
- **Repository:** petcare-evidence-repository (this repo)
- **Branch:** `gate-evidence-prep`

## What this repo declares

Quoted verbatim from `evidence/G-A1/MANIFEST.json`
(`timestamp: 2026-04-17T00:00:00Z`):

> "feature_flags": "All 4 AI feature flags default False — enable via env var
> only"

The same MANIFEST identifies the **code** location of the flag definitions
as `app/backend/config/feature_flags.py` — a file that lives in the Emergent
backend repository, **not** in this evidence repository.

## What this close can confirm

- The G-A1 MANIFEST exists and asserts default-False as the documented
  posture.
- This evidence repository does not contain any AI-feature code, feature-flag
  module, or AI-inference call site.
- A repository-wide grep for `feature.flag`, `FEATURE_FLAG`, `enableAi`,
  `ai.enabled`, `hitl.required` across `petcare_web/` and `petcare_api/`
  surfaces no matches (verified 2026-05-23 on `gate-evidence-prep`).

## What this close cannot confirm

- The **runtime** value of the four flags in the deployed Emergent backend
  container at `2026-05-23`. Verifying that requires reading the running
  config in the Emergent container or its source repository, neither of
  which is engineering close-out scope.
- That no out-of-band activation has occurred since the 2026-04-17 manifest
  was written.

## Required before PH-AI activation

Re-verification by the Infrastructure Lead with a signed runtime
attestation, deposited in this directory as `runtime_flag_attestation.txt`
and hashed into a sibling `MANIFEST_PH_AI.json` (built at landing, not now).

## No gate marked PASS

This document does not assert G-A1 closure. The G-A1 parent `MANIFEST.json`
status remains `AWAITING_HUMAN_CLOSURE`.
