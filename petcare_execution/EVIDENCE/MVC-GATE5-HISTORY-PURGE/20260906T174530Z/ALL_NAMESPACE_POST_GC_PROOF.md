# All-namespace proof — after GC

```
git reflog expire --expire=now --all
git gc --prune=now
```

## Object database, before and after

| | before | after |
|---|---|---|
| loose objects | 1038 | 0 |
| in-pack | 25372 | 9413 |
| pack size | 77.89 MiB | 8.89 MiB |
| `.git` on disk | 84 M | 9.6 M |

The old history is gone as objects, not merely unreferenced:

```
git cat-file -t 5202bb5ffbd6b3085cdeedc68c5e9ea876a0dc96
fatal: git cat-file: could not get object info
```

## Reachability

```
TOTAL_REFS = 96
ALL_NAMESPACE_CARRYING_AFTER_GC = 0
```

## Content

```
BLOBS_SCANNED                      = 5208
ALL_NAMESPACE_SECRET_BLOBS_AFTER_GC = 0
```

Raw output: `ALL_NAMESPACE_POST_GC_SCAN.txt`.

## How the scanner stayed armed after GC

The comparand is derived from the introducing commit, which this repository no
longer has. For the post-GC run the scanner was armed from the **mirror**, which
still retains the old history via its GitHub-managed `refs/pull/*` refs, and it
verified the derived value against the pinned fingerprint before scanning
(`COMPARAND_LENGTH_BYTES = 25`, digest check passes or the scanner aborts).

The pre-GC positive control remains the authoritative arming evidence. The
post-GC zero is not asked to carry that burden on its own.
