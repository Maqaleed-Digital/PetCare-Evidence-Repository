PACK_ID: PETCARE-PHASE-1-BUILD-EP04-WAVE-06

Completed:
- pharmacy/visibility.py created: review access audit surfaces + operational aggregation
- get_review_history_read_model(): review notes + audit trail + access audit envelope
- list_review_timeline_entries(): chronological audit trail with access audit envelope
- get_return_to_vet_follow_up_link(): follow-up required flag + reason code + identity guard
- get_review_disposition_registry(): locked registry of decision → status → outcome mappings
- get_operational_review_status_summary(): deterministic review/handoff/prescription status counts
- REVIEW_ACCESS_AUDIT_EVENTS (5) + RETURN_TO_VET_REASON_CODES (2) contracts locked
- 7 Wave-06 tests added and passing
- All 44 tests passing (7+6+8+8+8+7)

No prescription state mutated by visibility surfaces.
No protected-zone semantics modified.
No EP-01 / EP-02 / EP-03 baselines reopened.
No blocking logic introduced.
No AI autonomy introduced.

Validation:
44 passed / 0 failed (7+6+8+8+8+7)

Protected-zone semantics: unchanged
