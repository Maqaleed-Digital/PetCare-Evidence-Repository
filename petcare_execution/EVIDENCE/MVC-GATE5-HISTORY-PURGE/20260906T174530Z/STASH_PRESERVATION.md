# Stash preservation

```
STASH_SHA                       = da12e50d6b5ef2c95fda94bc662e29229e23af2f
STASH_REACHES_INTRODUCING_COMMIT = NO
STASH_RETIRED_SECRET_MATCHES     = 0
STASH_PRESERVED                  = YES
STASH_SECRET_RISK                = NO
```

## Contents

```
stash@{0}: On main: MVC-UX-WO-001 PO-FLAG: cloudbuild changes held out of pilot
branch (api: adds unconditional gcloud run deploy --allow-unauthenticated step;
web: switches _NEXT_PUBLIC_API_BASE_URL hostname to ...-llavmae4sq-wx...).
Examine separately before deploying.
```

This is **intentionally parked, unrelated work** carrying a live PO flag. It is
not Gate-5 material.

## Re-measured in this run

The armed scanner was run over every blob reachable from `refs/stash`
(4723 blobs): **0 matches**. The introducing commit is not an ancestor of the
stash. The two results are consistent — the stash's parent commit predates the
introduction of the literal.

## Not dropped

`git stash drop` was **not** executed. Gate 5 authorizes removal of retired-key
history; it does not authorize destruction of unrelated parked work. The stash
survived the reflog expiry and `gc --prune=now` because it is a live ref, and it
is still present at the SHA above.
