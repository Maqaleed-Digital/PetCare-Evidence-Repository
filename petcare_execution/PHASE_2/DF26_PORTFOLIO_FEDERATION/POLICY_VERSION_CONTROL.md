POLICY VERSION CONTROL — DF26

PURPOSE:
Ensure policy consistency across all units.

RULES:

1. SINGLE SOURCE OF POLICY TRUTH
2. VERSION LOCK REQUIRED
3. NO PARTIAL DEPLOYMENT

MODEL:

- policy_id
- version
- checksum
- effective_timestamp

ENFORCEMENT:

ALL UNITS MUST MATCH:
- policy version
- checksum

FAIL CONDITIONS:

IF VERSION MISMATCH:
→ BLOCK EXECUTION

IF CHECKSUM MISMATCH:
→ BLOCK EXECUTION

ROLLBACK:

- revert to last valid version
- revalidate all units
