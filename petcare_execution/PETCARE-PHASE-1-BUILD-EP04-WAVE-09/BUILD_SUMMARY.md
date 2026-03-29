PACK_ID: PETCARE-PHASE-1-BUILD-EP04-WAVE-09

Completed:
- pharmacy/contracts.py created: API_CONTRACT_VERSION + success_envelope() + error_envelope()
- pharmacy/registry.py created: READ_ONLY_ENDPOINT_REGISTRY (11 entries, mirrors Wave-08 READ_ONLY_API_SURFACES)
- pharmacy/api.py extended: normalize_response() + normalize_error() helpers via contracts import
- 3 Wave-09 tests added and passing
- All 55 tests passing (7+6+8+8+8+7+2+6+3)

No prescription state mutated.
No protected-zone semantics modified.
No EP-01 / EP-02 / EP-03 baselines reopened.

Validation:
55 passed / 0 failed (7+6+8+8+8+7+2+6+3)

Protected-zone semantics: unchanged
