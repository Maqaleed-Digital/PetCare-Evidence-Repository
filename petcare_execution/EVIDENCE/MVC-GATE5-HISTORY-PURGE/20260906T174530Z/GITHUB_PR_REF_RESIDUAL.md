# GitHub-managed refs — the residual this closeout cannot fix

```
REPOSITORY_VISIBILITY            = PUBLIC
RESIDUAL_GITHUB_MANAGED_REF_COUNT = 6
RESIDUAL_PUBLIC_DISCOVERABILITY   = CONFIRMED_ANONYMOUS
```

## Measurement

`git filter-repo` rewrites the refs a repository owns. It does not rewrite
`refs/pull/*/head`, which GitHub creates and controls. Those refs still point
at pre-rewrite commits.

Fetchability was tested **anonymously** — no token, no credential helper,
`GIT_TERMINAL_PROMPT=0` — against `https://github.com/…`, which is how an
outside party would reach them.

| ref | live SHA | publicly fetchable | carries old history |
|---|---|---|---|
| `refs/pull/1/head` | `ed4e0e36c8bada260d91d5d52c6d26531731d2cc` | **YES** | **YES** |
| `refs/pull/2/head` | `2b3e7b2a6b08c3cd948557c95d2af7e65b6b5e53` | **YES** | **YES** |
| `refs/pull/3/head` | `9fc8e2494043fffa11d044942bc66ec9d8c5b65f` | **YES** | **YES** |
| `refs/pull/4/head` | `793c64b93b86cce35b7ad06044de12015ce6721c` | **YES** | **YES** |
| `refs/pull/5/head` | `b8b5014e5a1f6848cfb6022034c77485dc2c0f3b` | **YES** | **YES** |
| `refs/pull/6/head` | `e78159b285a7719759941421941b04ef0ab08ee1` | **YES** | **YES** |

Live SHAs are identical to the mirror snapshot, so the mirror scan below is a
scan of the live content.

## The literal is still reachable from them

The armed scanner, run over these six refs:

```
BLOBS_SCANNED     = 5031
MATCHING_BLOBS    = 10
MATCHING_PATHS    = 5
TOTAL_OCCURRENCES = 22
```

That is the **same 10 blobs and 5 paths** the positive control found in old
history. Raw output: `GITHUB_PR_REF_RESIDUAL_SCAN.txt`.

These refs were measured and **not mutated**, per the Gate-5 instruction.

## The honest statement

- The retired literal **was publicly fetchable from owned branch history before
  Gate 5**.
- Owned branch history is **now remediated** — 0 secret blobs across all 42
  owned origin refs, introducing commit unreachable.
- **Surviving GitHub-managed refs remain publicly discoverable where measured** —
  six of them, all six still exposing the literal.
- **W0-A2 rejects the retired key at runtime**, by fingerprint, so possession of
  the literal does not yield a usable signing key against current `main`.
- **External clones cannot be recalled.** Anyone who cloned before the purge, or
  who fetches `refs/pull/*` now, holds the literal. `UNKNOWN_EXTERNAL_CLONES = YES`.

The residual is why `SUPPORT_REQUEST_REQUIRED = YES`
(`GITHUB_SUPPORT_REQUEST.md`), and why the runtime guard, not the purge, is the
control that actually closes the risk.
