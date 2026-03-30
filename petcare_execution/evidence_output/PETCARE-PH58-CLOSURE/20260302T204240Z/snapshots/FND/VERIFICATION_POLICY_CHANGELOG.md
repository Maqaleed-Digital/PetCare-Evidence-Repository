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
PH56|20260302T201929Z|ALLOWLIST_ADD|pack=PETCARE-PH44B-CLOSURE|policy_sha256=d7f3a16dc4969e97c89624513085fe6256ff05dde8532f2ef000f9d9345df9e5
PH56|20260302T203942Z|ALLOWLIST_ADD|pack=PETCARE-PH45B-CLOSURE|policy_sha256=aa77d720db9be54fe6bc26ea537bdcc451ccec04d44ab6cad80124f3e5c75668
PH56|20260302T204240Z|ALLOWLIST_ADD|pack=PETCARE-PH54-CLOSURE|policy_sha256=4803edb67276c231366d72686643225bebf6485681581e7c65d5a2154004228a
