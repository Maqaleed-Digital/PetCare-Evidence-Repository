# GitHub Support request — draft (not submitted)

```
SUPPORT_REQUEST_DRAFTED = YES
SUBMITTED               = NO
```

Drafted for a human to submit. This closeout does not submit it: that is an
external dashboard action.

---

## Subject

Purge cached pull-request refs after a completed history rewrite — **PUBLIC
repository**

## Repository

**`Maqaleed-Digital/PetCare-Evidence-Repository`** — visibility: **PUBLIC**

## Summary

We completed an authorized history rewrite of this repository to remove a
retired credential literal from its git history. The rewrite of **owned branch
history succeeded**: the literal is no longer reachable from any of our 42
branches, and the commit that introduced it is unreachable from every one of
them.

However, the GitHub-managed pull-request refs still point at pre-rewrite
commits, and those commits still contain the literal. We have verified that
these refs are fetchable **anonymously**, without authentication.

## Surviving refs we are asking about

All six currently resolve and expose pre-rewrite history:

```
refs/pull/1/head  ed4e0e36c8bada260d91d5d52c6d26531731d2cc
refs/pull/2/head  2b3e7b2a6b08c3cd948557c95d2af7e65b6b5e53
refs/pull/3/head  9fc8e2494043fffa11d044942bc66ec9d8c5b65f
refs/pull/4/head  793c64b93b86cce35b7ad06044de12015ce6721c
refs/pull/5/head  b8b5014e5a1f6848cfb6022034c77485dc2c0f3b
refs/pull/6/head  e78159b285a7719759941421941b04ef0ab08ee1
```

## Commit that introduced the material

```
5202bb5ffbd6b3085cdeedc68c5e9ea876a0dc96
```

## Identifying the material without disclosing it

We identify the retired value **only** by digest. We are not transmitting the
value itself.

```
SHA-256 of the retired literal:
1cdd7efa59d45698ceba9652ee1c22aa7472503ee381af56833df8f98d65f4ca
```

## Request

Please purge or invalidate the pull-request refs listed above, together with any
related cached objects and cached web views (commit, diff and blob pages) that
still serve pre-rewrite content for this repository, to the extent supported.

## Current state, for context

- Owned branch history: remediated and verified.
- `main` head tree is byte-identical to its pre-rewrite tree — the rewrite
  changed history, not the code.
- Branch protection was restored to a byte-identical configuration.
- The retired key is **rejected at runtime** by a fingerprint-based guard, so it
  is not a usable credential against current code.
- We understand clones already taken cannot be recalled.

## Not included

The plaintext literal is deliberately absent from this request. Please do not
ask us to transmit it; the digest above is sufficient to identify it.
