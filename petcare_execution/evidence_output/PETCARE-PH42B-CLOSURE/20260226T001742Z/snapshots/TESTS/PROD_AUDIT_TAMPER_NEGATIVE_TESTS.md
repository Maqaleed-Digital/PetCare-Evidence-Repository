PetCare PH42-B
Production Audit Ledger Tamper Negative Tests

NEG-AUD-01 Modify payload field in record 3
Expected: verifier FAIL with RECORD_HASH_MISMATCH

NEG-AUD-02 Modify prev_hash of record 4
Expected: verifier FAIL with PREV_HASH_MISMATCH

NEG-AUD-03 Delete record 2
Expected: verifier FAIL with SEQ_MISMATCH or PREV_HASH_MISMATCH

NEG-AUD-04 Reorder record lines
Expected: verifier FAIL with SEQ_MISMATCH

NEG-AUD-05 Insert new record in middle without recomputing chain
Expected: verifier FAIL

Notes
PH42-B provides deterministic verification for tamper-evidence. Signing of bundles is handled in later phase.
