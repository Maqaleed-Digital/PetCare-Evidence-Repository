# Verification Policy Changelog (Governed)

This changelog is REQUIRED whenever any of the following files change:
- `FND/VERIFICATION_POLICY.json`
- `FND/VERIFICATION_POLICY.sha256`

## Entry Format (MUST)
Append a new entry block at the bottom containing:
- `ts_utc=<YYYYMMDDTHHMMSSZ>`
- `policy_sha256=<64-hex>`  (must equal the content of `FND/VERIFICATION_POLICY.sha256`)
- `summary=<short reason>`
- `approved_by=<name|role>` (optional but recommended)

Example:
ts_utc=20260302T200000Z
policy_sha256=0123...abcd
summary=Allowlisted PETCARE-PH44B-CLOSURE for meta verifications
approved_by=CEO
---

## Entries

ts_utc=20260302T185000Z
policy_sha256=c60ce1a1d4a86506faef03561e2f22c902aa80986c48804e03d3b57478dcfa17
summary=PH52 initial policy created (empty allowlist; all meta verifications blocked by default)
approved_by=PH52
---
