# Web tree authority — `petcare_web` vs `petcare-web`

**Date:** 2026-09-03 · **Authority:** MVC-GOV-CANON-001
**Closes:** `WEB_TREE_DUPLICATION_OPEN`

## Determination

```
CANONICAL_WEB_TREE            = petcare_web
SECONDARY_WEB_TREE            = petcare-web
SECONDARY_DISPOSITION         = SUPERSEDED_PROTOTYPE
WEB_TREE_AUTHORITY_STATUS     = RESOLVED
```

## Evidence

| | `petcare_web` | `petcare-web` |
|---|---|---|
| Next / React | 14.2.25 / 18.3.1 | **16.1.6 / 19.2.3** |
| Scripts | dev, build, start, lint, **typecheck, test, e2e** | dev, build, start, lint |
| Test files | **15** | **0** |
| Playwright | **yes** | no |
| Dockerfile | **yes** | **no** |
| cloudbuild.yaml | **yes** | **no** |
| Tracked files | 71 | 79 |
| Last change | **2026-09-03** (today) | 2026-04-07 |

## Reasoning

The naming is the least informative signal and was deliberately ignored. So is
dependency version: `petcare-web` carries *newer* Next and React, which is the
one fact that superficially favours it and is exactly why it needed checking
rather than assuming.

What settles it is that `petcare-web` **cannot be built or deployed and is not
tested**: no Dockerfile, no cloudbuild, no test script, no typecheck, no
Playwright. It has no verification and no path to production. It was last
touched on 2026-04-07 and has been untouched through every subsequent wave —
WO-001, WO-002, wave-0 hardening and PORT-03 all landed in `petcare_web`.

That is the signature of a prototype spike that was started on newer
dependencies and then abandoned, not of a successor.

## Consequence for the port plan

All of PORT-04, PORT-05 and PORT-06 target **`petcare_web`**. The existing
Playwright configuration there is the single canonical harness; no second
harness is to be created, and no functionality is to be ported into both trees.

`petcare-web` is left in place and untouched. Deleting it is a separate
disposal decision with its own evidence requirement, and nothing in this lane
needs it gone.
