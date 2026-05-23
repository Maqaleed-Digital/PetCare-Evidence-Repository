# G-A1 — PH-AI Evidence Landing

Scaffold for the PH-AI work-stream's evidence pack. PH-AI is the AI-governance
expansion track and is currently **HELD** in line with the policy that pilot
proof outranks AI-governance expansion. This directory exists so that, when
PH-AI is taken off hold, its evidence has a manifest-tracked destination.

## Status

`HELD` — PH-AI is not active. AI features are not built in this evidence
repository, and PH-AI activation is gated on pilot-proof acceptance, which is
out of engineering scope for this close.

The G-A1 parent `MANIFEST.json` status remains `AWAITING_HUMAN_CLOSURE`. This
scaffold does not change that.

## AI feature-flag state (as-declared)

See `feature_flag_state.md` for the full snapshot. Short form: the parent
`MANIFEST.json` declares that all four AI feature flags default to `False`
and require an explicit environment variable to enable. The source of truth
for the runtime flag values lives in the Emergent backend repository at
`app/backend/config/feature_flags.py` and is **not** stored in this evidence
repository. Re-verification at activation time is required and is not
performed by this close.

## What lands here when PH-AI activates

See `INTAKE_INDEX.md` for the full list. At a glance:

- Runtime flag-state attestation (signed snapshot from the Emergent
  container, anchored by SHA-256 in a sibling `MANIFEST_PH_AI.json`).
- HITL queue audit sample (any human-in-the-loop intervention rows).
- Prompt / output hash log (SHA-256 only — raw prompt and raw output are
  never stored, per the parent manifest's stated constraint).
- Gate-dashboard SLO observations (`GET /api/gates` latency / availability).
- Pilot-proof attestation that PH-AI expansion is unblocked.

## Do NOT

- Build AI features in this directory. The directive is explicit: scaffold
  the evidence landing only.
- Activate any AI feature flag from this close. Flags stay where they are.
- Mark G-A1 `PASS`. Gate closure is a human decision and is outside the scope
  of this close.
- Deposit prompt or output text in this directory. Even for testing — hashes
  only.
