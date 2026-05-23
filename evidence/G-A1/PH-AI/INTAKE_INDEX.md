# PH-AI Intake — Expected Artefacts

Filenames that PH-AI evidence MUST adopt when deposited in
`evidence/G-A1/PH-AI/`. The PH-AI manifest builder (run by the AI-Governance
Owner at landing time) keys on these names to produce a SHA-256-anchored
`MANIFEST_PH_AI.json`.

| Filename                          | Required | Description                                                                                  |
| --------------------------------- | -------- | -------------------------------------------------------------------------------------------- |
| `runtime_flag_attestation.txt`    | yes      | Signed snapshot of the 4 AI feature flags from the deployed Emergent backend container.      |
| `hitl_queue_audit.json`           | yes      | Sample of HITL queue rows: state transitions, approver identity, timestamps.                 |
| `prompt_output_hash_log.json`     | yes      | SHA-256 only — never raw prompt or output. Per parent MANIFEST stated constraint.            |
| `gate_dashboard_sla.md`           | yes      | SLO observations from `GET /api/gates` over a stated window (latency, availability).         |
| `ph_ai_pilot_proof.md`            | yes      | Evidence that the pilot proof unblocking PH-AI has landed (pilot proof outranks expansion).  |
| `ai_decision_log_sample.json`     | optional | Sampled `log_ai_decision()` entries (hashes only).                                           |

## `hitl_queue_audit.json` schema (one entry per HITL row)

```
{
  "row_id": "<uuid>",
  "ai_decision_hash": "<sha256>",
  "state": "queued | approved | rejected | expired",
  "approver_role": "platform_admin",
  "queued_at": "<ISO-8601>",
  "resolved_at": "<ISO-8601 or null>"
}
```

## `prompt_output_hash_log.json` schema

```
{
  "decision_id": "<uuid>",
  "model_name": "<vendor:model>",
  "prompt_sha256": "<hex>",
  "output_sha256": "<hex>",
  "occurred_at": "<ISO-8601>",
  "hitl_required": true | false
}
```

**No `prompt_text` or `output_text` field is permitted.** The MANIFEST builder
MUST refuse to hash an entry that carries either.

## Naming hygiene

- All filenames lowercase except `MANIFEST_PH_AI.json` (sibling, generated).
- ISO-8601 timestamps with `Z` suffix.
- No PII in any filename, ever.

## Do NOT submit fabricated content

PH-AI is currently **HELD**. Until pilot proof unblocks it, no real artefacts
will exist. Any rehearsal deposits MUST use a `_DRYRUN_` prefix and the
MANIFEST builder MUST refuse to compute hashes for them.
