# Protection window

```
PROTECTION_WINDOW_SECONDS   = 15
TEMPORARILY_RELAXED_CONTROLS = 2

1. REQUIRED_STATUS_CHECKS
2. ALLOW_FORCE_PUSHES

RESTORED_REQUIRED_CHECK        = verify
RESTORED_REQUIRED_CHECK_APP_ID = 15368
```

## What the window actually relaxed

`PROTECTION_WINDOW.json`, verbatim:

```json
{
  "allow_deletions": false,
  "allow_force_pushes": true,
  "allow_fork_syncing": false,
  "block_creations": false,
  "enforce_admins": true,
  "lock_branch": false,
  "required_conversation_resolution": false,
  "required_linear_history": false,
  "required_pull_request_reviews": null,
  "required_status_checks": null,
  "restrictions": null
}
```

Exactly two controls moved from their steady state:

| control | steady | during window |
|---|---|---|
| `required_status_checks` | `{strict: true, checks: [verify/15368]}` | `null` |
| `allow_force_pushes` | `false` | `true` |

Everything else — including `enforce_admins: true` — was held at its steady
value **throughout** the window. Admin enforcement was never dropped.

## Duration

15 seconds, as measured by the Sponsor during the transaction. This closeout
carries that measurement rather than re-deriving it; the window had already
closed before this run began, so it is not independently re-measurable here.
That is stated rather than presented as a fresh observation.

## Restoration

`PROTECTION_RESTORE.json` rebinds `verify` at `app_id 15368` with
`strict: true`. The live read after restoration is byte-identical to the read
before the window (`PROTECTION_NORMALIZATION.md`).
