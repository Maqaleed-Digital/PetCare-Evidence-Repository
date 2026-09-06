# main HEAD tree identity

The primary Gate-5 safety proof: the rewrite changed history, not the code that
history produces.

```
PRE_PURGE_MAIN      = 24de5399abc37cc9d53308d4e358ac19ecaa5ad1
PRE_PURGE_MAIN_TREE = a46ee9f034882eab0bd730b3cf59e5df5c5a1c67

REWRITTEN_MAIN      = 3cef8f9db73a07aab33e953ac7d41c8b238d159d
REWRITTEN_MAIN_TREE = a46ee9f034882eab0bd730b3cf59e5df5c5a1c67

MAIN_HEAD_TREE_IDENTICAL = YES
git diff --name-status 24de5399 3cef8f9d  ->  0 lines
```

The two trees are the **same object**, not merely equivalent. The working tree
at the tip of `main` is byte-for-byte what it was before the purge.

## Why this is asserted for `main` only

The five non-main historical tips carried the plaintext **at HEAD**, not only
in ancestry. `filter-repo` necessarily redacted their tip content, so their
trees were expected to change and did. Requiring tree identity there would be
requiring the purge not to have worked.

Tree identity is therefore the right assertion for `main` and the wrong one for
the five. What is asserted for all six, and for the other 36 owned branches, is
the absence of the literal and the unreachability of the introducing commit.

## Why a green suite is not this proof

`GATE5_RESUME_CONDITIONS.md` records the failure mode from the first attempt:
`filter-repo` mutates implementation and its tests together, so a rewrite that
disarms a guard can still show a fully green suite. The first rehearsal passed
150 tests on a tree that **accepted the retired key**.

Tree identity at `main` closes that hole directly: `main` carries the W0-A2
fingerprint guard, and its tree is unchanged, so the guard at `main` is
provably the same guard that was reviewed and merged. Tests are secondary
evidence here, and are recorded as such.
