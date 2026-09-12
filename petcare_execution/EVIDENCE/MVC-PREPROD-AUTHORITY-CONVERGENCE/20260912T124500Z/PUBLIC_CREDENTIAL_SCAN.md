# A19 — live application credential literals

```
FILES_SCANNED=239
LIVE_APPLICATION_CREDENTIAL_LITERAL_COUNT=0
```

Scanned: `petcare_api`, `petcare_runtime/src`, `scripts`, `petcare_web/{app,lib,components}`
and `middleware.ts`, excluding tests and `node_modules`, with comments stripped.
Pattern: any `*password*` / `*passwd*` / `*pwd*` / `*secret_key*` / `*api_key*` /
`*token*` name assigned a string literal, excluding `*_hash` (a stored digest is
not a credential).

| Check | Result |
|---|---|
| the retired seed password in any tracked serving file | **0** |
| a default `SECRET_KEY` literal | **0** — W0-A removed it; `secret_provider` has no fallback |
| a default DB password literal | **0** — the URL comes from the governed secret source |
| a session-signing default | **0** |

The two deterministic non-secret values that remain are in test bootstrap
(`conftest.py`) and CI, both labelled as such and neither read by a deployed
process.

## Historical exposure is NOT closed by this result

```
GITHUB_SUPPORT_REFS_PULL_1_6=NOT_SENT
```

The retired credential is gone from the working tree. It remains in this
repository's **git history**, and the repository is PUBLIC. Removing it from the
tree does not remove it from a clone, a fork, or a cached object — and the
identities it belonged to have been discarded precisely so that the published
value can never become a production credential.

That is the mitigation available to an engineering lane. The history track is an
external-account action and is untouched here, not claimed closed, and not
attempted.
