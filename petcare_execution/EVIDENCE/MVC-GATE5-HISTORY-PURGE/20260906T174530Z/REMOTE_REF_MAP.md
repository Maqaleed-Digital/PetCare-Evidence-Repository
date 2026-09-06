# Remote ref map — live origin, read after publication

`git fetch --prune origin` reported a forced update on exactly six refs, and
each landed on the SHA the commit-map assigns it.

| branch | rewritten SHA | live | verdict |
|---|---|---|---|
| `main` | `3cef8f9db73a07aab33e953ac7d41c8b238d159d` | same | MATCH |
| `gate-evidence-prep` | `4986725505de0af9e37b2854c170e364b1075cff` | same | MATCH |
| `m8-brand-cleanup` | `770eb193fda6cdcbe41a7fa19e9b8caafb02bd23` | same | MATCH |
| `mvc-ux-wo-001` | `2e9c070468316b0cc6b3d259dd973b6606ea4e41` | same | MATCH |
| `mvc-ux-wo-002-trust-surfaces` | `2e06ecf992a40ddd5b54ce13189755b1b6ec9351` | same | MATCH |
| `security/w0a-require-session-signing-key` | `a838d9f2b43e7cdcee659fab9729915533b78884` | same | MATCH |

```
ORIGIN_MAIN                  = 3cef8f9db73a07aab33e953ac7d41c8b238d159d
NON_MAIN_REMOTE_MAP_VERIFIED = 5/5
REMOTE_REF_MAP_VERIFIED      = YES
```

## The other 36 owned origin branches

The repository carries 42 owned branches in total. The 36 not listed above were
**not** rewritten, because they never contained the literal: `filter-repo` left
their tips byte-identical, and the introducing commit is not an ancestor of any
of them. That is asserted, not assumed — every one of the 42 was tested:

```
OWNED_ORIGIN_REFS_TESTED           = 42
POST_PUSH_CARRYING                 = 0
SECRET_BLOBS_REACHABLE_ORIGIN      = 0   (5206 blobs scanned)
INTRODUCING_COMMIT_REACHABLE_OWNED_REFS = NO
PURGE_COMPLETE_OWNED_REFS          = YES
```

Raw scanner output: `REWRITTEN_HISTORY_SCAN.txt`.
