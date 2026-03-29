PACK_ID: PETCARE-PHASE-1-BUILD-EP04-WAVE-08

Completed:
- pharmacy/api.py created: read-only API exposure layer (11 endpoint surfaces)
- _read_only_envelope(): deterministic surface/read_only/actor_user_id/payload wrapper
- all surfaces delegate to repository → query/visibility/handoff layers; no new logic
- READ_ONLY_API_SURFACES (11): contract locked
- __init__.py updated to export all Wave-08 symbols
- 5 Wave-08 tests added and passing
- All 51 tests passing (7+6+8+8+8+7+2+5)

Note: api.py uses dataclasses.asdict() for PrescriptionQueueEntry (no to_dict() method).
No prescription state mutated by API layer.
No protected-zone semantics modified.
No EP-01 / EP-02 / EP-03 baselines reopened.
No blocking logic introduced.
No AI autonomy introduced.

Validation:
51 passed / 0 failed (7+6+8+8+8+7+2+5)

Protected-zone semantics: unchanged
