# G-A1 — AI Governance Policy

## Scope

All AI-assisted features (diagnosis, prescription recommendation, triage scoring, owner chat) must:
1. Log every inference via `log_ai_decision()` before returning output to any user
2. Never expose AI output directly for clinical decisions without HITL approval where `hitl_required=True`
3. Be gated behind a feature flag (all flags default `False` for pilot)

## Logging Requirements (P08-S1)

Every `AILog` row must include:
| Field | Requirement |
|-------|------------|
| `prompt_hash` | SHA-256 of exact prompt sent to model |
| `output_hash` | SHA-256 of raw model output |
| `model_version` | Exact model ID string |
| `latency_ms` | Wall-clock time of inference call |
| `safety_filter_triggered` | Whether output was filtered/redacted |
| `hitl_required` | Whether human review gate applies |

Prompt and output are never stored in plaintext — only their SHA-256 hashes.

## HITL Queue Rules (P08-S2)

### When `hitl_required=True`:
- A `HITLQueue` row is created automatically alongside the `AILog`
- AI output **must not** be actioned (e.g., dispensed, signed) until queue item is `approved`
- Initial status is always `pending`

### Approval:
- Only `platform_admin` role may approve or reject
- Approval back-fills `AILog.hitl_approved_by` and `hitl_approved_at`
- Emits `hitl.approved` audit event

### Rejection:
- `rejection_reason` is mandatory (non-empty)
- Emits `hitl.rejected` audit event with reason

### Features that ALWAYS require HITL:
- `ai_prescription` — any automated medication recommendation
- `ai_diagnosis` — differential diagnosis list presented to vet as definitive

## Feature Flag Policy (P08-S4)

All flags default `False`. Enablement requires:
1. Written approval from Medical Director (for clinical flags)
2. Platform Director sign-off
3. Environment variable set in deployment manifest (not code)

| Flag | Clinical? | Requires HITL |
|------|-----------|--------------|
| `ai_diagnosis` | Yes | Yes |
| `ai_prescription` | Yes | Yes |
| `ai_triage` | Yes | No (advisory scoring only) |
| `ai_chat` | No | No (general wellness only) |

## Gate Dashboard

`GET /api/gates` (platform_admin only) surfaces:
- All 8 recovery gates with test counts and status
- Live feature flag state
- Governance note: "Gate closure is a human authority action."
