PACK_ID: PETCARE-PHASE-1-BUILD-EP04-WAVE-07

Completed:
- pharmacy/repository.py created: PharmacyRepository in-memory store
  - add_prescription() / add_review() / get_prescription() / get_review()
  - list_reviews_by_prescription_id() / list_reviews_by_consultation_id() / list_reviews_by_tenant_id()
  - all listing methods deterministically sorted by created_at / review_id
- pharmacy/query.py created: composition query layer
  - get_full_review_context(): prescription + review + handoff + history in one read
  - list_reviews_for_prescription(): review IDs + count by prescription
- 2 Wave-07 tests added and passing
- All 46 tests passing (7+6+8+8+8+7+2)

No prescription state mutated by repository or query layer.
No protected-zone semantics modified.
No EP-01 / EP-02 / EP-03 baselines reopened.
No blocking logic introduced.
No AI autonomy introduced.

Validation:
46 passed / 0 failed (7+6+8+8+8+7+2)

Protected-zone semantics: unchanged
