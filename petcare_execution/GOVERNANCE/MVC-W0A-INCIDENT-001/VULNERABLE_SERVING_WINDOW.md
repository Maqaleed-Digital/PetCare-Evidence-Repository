# Vulnerable serving window — derivation

**Method:** `git log -S` over the retired literal across all refs, plus file-creation
audit and deployment-evidence sweep. Dates are commit-author dates (ISO, +0300).

## The literal's life in source

| Event | Commit | Date | Evidence |
|---|---|---|---|
| **Introduced** | `5202bb5f` "feat(api,auth): wire pilot auth router into deploying petcare_api" | **2026-05-23** | `petcare_api/routers/auth.py` created in this commit (**+164 lines, new file**); line 14 was `SECRET_KEY = os.getenv("SECRET_KEY", "<RETIRED_LITERAL>")` |
| Pushed to PUBLIC remote | `e93e083b` (origin/main tip) | **2026-05-24** | GitHub `pushedAt = 2026-05-23T22:22:51Z` |
| **Removed** | `3224c65d` / `e98ee966` "W0-A: require the session signing key" | **2026-09-01** | fail-closed `_require_secret_key()` |
| Fix pushed to public remote | — | **NEVER** | `origin/main` still contains the literal |

`git log --follow` confirms `petcare_api/routers/auth.py` has **no history before
`5202bb5f`**. The file did not exist prior to 2026-05-23.

## CORRECTION — `VULNERABLE_IMAGE_EXECUTED` reverts YES → UNKNOWN

`NOTION_AUTHORITY_SYNC.md` (CONTRADICTION 2) concluded:

> "This deployment **predates W0-A by five months**, so the serving API carried
> `os.getenv("SECRET_KEY", "<default>")` unless `SECRET_KEY` was set."

The reasoning fixed on the wrong end of the window. It is true that the PH5.1
deployment predates the *fix*. But it also predates the *defect*:

```
2026-04-06   PH5.1 — SYSTEM_STATE=PRODUCTION_ACTIVE (web + api)
                  ^ seven weeks BEFORE the vulnerable file existed
2026-05-23   vulnerable literal introduced (auth.py created)
2026-09-01   W0-A removes it
```

**The image deployed on 2026-04-06 could not have contained code that did not yet
exist.** PH5.1 therefore does not evidence execution of the vulnerable artefact,
and the inference that promoted `VULNERABLE_IMAGE_EXECUTED` to `YES (evidenced)`
does not hold. It returns to `UNKNOWN`.

## Is there any deployment after 2026-05-23?

No evidence of one exists in this repository:

- No commit touches `petcare_api/`, `cloudbuild.yaml` or `deploy_ui_gcp.sh` between
  2026-05-23 and the W0 fixes of 2026-09-01.
- The newest deployment/build evidence bundles are dated **April 2026**. The only
  post-May evidence directories are today's governance runs.
- `petcare-web-prod` has since been **deleted** (negative-control 404); `petcare-api-prod`
  exists but serves **no healthy revision**.

Absence of local evidence is not proof of no deployment — Cloud Build and Cloud Run
revision history are authoritative and are credential-gated. But nothing on this
side supports one.

## Window

```
VULNERABLE_CODE_INTRODUCED            = 2026-05-23              KNOWN
VULNERABLE_CODE_REMOVED_IN_SOURCE     = 2026-09-01              KNOWN
PUBLIC_SOURCE_EXPOSURE_OPENED         = 2026-05-23T22:22:51Z    KNOWN
PUBLIC_SOURCE_EXPOSURE_CLOSED         = NOT CLOSED — still live on origin/main
PUBLIC_SOURCE_EXPOSURE_DURATION       = 103 days and counting   KNOWN
FIRST_PRODUCTION_DEPLOYMENT (any code)= 2026-04-06              KNOWN
DEPLOYMENT_OF_VULNERABLE_CODE         = UNKNOWN  (no evidence either way)
LAST_KNOWN_VULNERABLE_DEPLOYMENT      = UNKNOWN
VULNERABLE_SERVING_WINDOW             = UNKNOWN — upper bound 2026-05-23 → 2026-09-01
                                        IF any deployment occurred in it
```

No deployment date has been invented. Where evidence is absent the value is
`UNKNOWN`, never `NO`.
