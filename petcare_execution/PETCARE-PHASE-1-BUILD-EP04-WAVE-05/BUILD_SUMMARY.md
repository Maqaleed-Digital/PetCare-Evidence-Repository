PACK_ID: PETCARE-PHASE-1-BUILD-EP04-WAVE-05

Completed:
- pharmacy/handoff.py created: review-to-dispense queue handoff boundary
- ReviewHandoffRecord frozen dataclass with deterministic to_dict()
- build_review_handoff_record(): prescription + review record → handoff record (identity guard)
- get_review_handoff_read_model(): boundary-only read model
- list_review_handoff_records(): sorted by created_at / review_id; prescription-review join
- get_latest_review_decision_summary(): latest note + outcome + warning count summary
- list_ready_for_dispense_queue_from_reviews(): filters READY_FOR_DISPENSE_QUEUE reviews only
- REVIEW_HANDOFF_AUDIT_EVENTS (3) + REVIEW_HANDOFF_OUTCOMES (3) contracts locked
- __init__.py updated to export all Wave-05 symbols
- 8 Wave-05 tests added and passing
- Wave-01 (7) + Wave-02 (6) + Wave-03 (8) + Wave-04 (8) + Wave-05 (8) all passing

No prescription state mutated by handoff boundary.
No protected-zone semantics modified.
No EP-01 / EP-02 / EP-03 baselines reopened.
No blocking logic introduced.
No AI autonomy introduced.

Validation:
37 passed / 0 failed (7+6+8+8+8)

Protected-zone semantics: unchanged
