# Local `main` reconciliation

```
LOCAL_MAIN_OLD_FULL    = e93e083b61f9833e7a8cd108df05647a162f6a37
LOCAL_MAIN_MAPPED_FULL = 4f36096bbe23de48b61ead9a20446b1b00366774
LOCAL_MAIN_RECONCILED  = YES
```

The full old SHA was read from the live local ref and the full mapped SHA from
the commit-map. Both reproduce the frozen T0 prediction
(`e93e083b… -> 4f36096bbe23de48b61ead9a20446b1b00366774`) exactly.

Applied by compare-and-swap:

```
git update-ref refs/heads/main 4f36096bbe23de48b61ead9a20446b1b00366774 e93e083b61f9833e7a8cd108df05647a162f6a37
```

Local `main` was **not** pointed directly at rewritten `origin/main`. The
commit-map names `4f36096b…`, and that is where the ref was placed. The mapped
commit was independently confirmed to be an ancestor of `origin/main`.

## Subsequent fast-forward, recorded separately

After the mapped reconciliation was complete and recorded, local `main` was
fast-forwarded normally to `origin/main`:

```
git merge --ff-only origin/main
LOCAL_MAIN_AFTER_FF = 3cef8f9db73a07aab33e953ac7d41c8b238d159d
```

This is an ordinary, non-destructive fast-forward along an ancestry that was
verified first. It is logged as a **separate act** from the reconciliation so
that the reconciliation evidence stands on its own and cannot be mistaken for
"local main was simply slammed to origin/main".

It also restored the working copy, which mattered: see the AUTH-11 note in
`FRESH_CLONE_VERIFICATION.md`.
