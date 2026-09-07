# Rewritten history scan — the armed zero

Same scanner, same session, same fingerprint as the positive control. Only the
ref set differs.

## Owned origin refs

```
OWNED_ORIGIN_REFS_TESTED                = 42
BLOBS_SCANNED                           = 5206
SECRET_BLOBS_REACHABLE_ORIGIN           = 0
MATCHING_PATHS                          = 0
POST_PUSH_CARRYING                      = 0
INTRODUCING_COMMIT_REACHABLE_OWNED_REFS = NO
PURGE_COMPLETE_OWNED_REFS               = YES
```

Every one of the 42 owned branches was tested individually for reachability of
`5202bb5ffbd6b3085cdeedc68c5e9ea876a0dc96`. None reaches it.

## The differential, side by side

| ref set | blobs | secret blobs | paths |
|---|---|---|---|
| retained OLD history (20 refs) | 5039 | **10** | **5** |
| owned origin, rewritten (42 refs) | 5206 | **0** | 0 |
| all local namespaces, pre-GC (96 refs) | 5208 | **0** | 0 |
| all local namespaces, post-GC (96 refs) | 5208 | **0** | 0 |
| GitHub-managed `refs/pull/1..6/head` | 5031 | **10** | **5** |

The instrument distinguishes in both directions inside a single run. It finds
the literal where the literal is, and does not find it where the purge removed
it. The last row is the residual this closeout cannot fix — see
`GITHUB_PR_REF_RESIDUAL.md`.

Raw output: `REWRITTEN_HISTORY_SCAN.txt`.
