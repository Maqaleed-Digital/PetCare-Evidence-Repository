# Sponsor publish receipt — as lodged, and as independently verified

The Sponsor executed the publication. The right-hand column is this closeout
run re-reading the live remote afterwards, not a restatement of the receipt.

| field | Sponsor receipt | independently verified |
|---|---|---|
| PRE_MAIN | `24de5399abc37cc9d53308d4e358ac19ecaa5ad1` | matches frozen T0 |
| NEW_MAIN | `3cef8f9db73a07aab33e953ac7d41c8b238d159d` | `git rev-parse origin/main` — same |
| NON_MAIN_PUSHED | 5/5 | 5/5 by `git ls-remote` (`REMOTE_REF_MAP.md`) |
| MAIN_FORCE_PUSH | YES | consistent with the forced-update fetch |
| PROTECTION_WINDOW_SECONDS | 15 | carried from the Sponsor measurement |
| PROTECTION_RESTORED_IDENTICAL | YES | `before.json` / `after.json` byte-identical |
| REQUIRED_CHECK | verify | live read = `verify` |
| REQUIRED_CHECK_APP_ID | 15368 | live read = `15368` |
| PUBLISH_TRANSACTION | COMPLETE | confirmed |

```
SPONSOR_PUBLISH_VERIFIED = YES
```

The four protection responses are reproduced verbatim in this pack as
`PROTECTION_BEFORE.json`, `PROTECTION_WINDOW.json`, `PROTECTION_RESTORE.json`
and `PROTECTION_AFTER.json`.
