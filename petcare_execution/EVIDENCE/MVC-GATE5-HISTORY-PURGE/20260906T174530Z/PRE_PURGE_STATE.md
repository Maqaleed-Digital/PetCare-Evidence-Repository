# Pre-purge state

```
PRE_PURGE_MAIN        = 24de5399abc37cc9d53308d4e358ac19ecaa5ad1
REWRITTEN_MAIN        = 3cef8f9db73a07aab33e953ac7d41c8b238d159d
INTRODUCING_COMMIT    = 5202bb5ffbd6b3085cdeedc68c5e9ea876a0dc96
RETIRED_SECRET_SHA256 = 1cdd7efa59d45698ceba9652ee1c22aa7472503ee381af56833df8f98d65f4ca
REPOSITORY            = Maqaleed-Digital/PetCare-Evidence-Repository
REPOSITORY_VISIBILITY = PUBLIC
```

The retired literal is referred to **only** by its SHA-256 fingerprint. It is
not reproduced in this pack, in any file this run wrote, or on any command line
this run executed.

## What was exposed, stated plainly

The retired `SECRET_KEY` literal was committed at
`5202bb5ffbd6b3085cdeedc68c5e9ea876a0dc96` and was, before Gate 5, **publicly
fetchable from owned branch history of a public repository**. That is a real
exposure that happened. The purge removes the literal from owned refs; it
cannot un-publish what was already fetchable, and it cannot recall clones taken
in the interval. See `GITHUB_PR_REF_RESIDUAL.md`.
