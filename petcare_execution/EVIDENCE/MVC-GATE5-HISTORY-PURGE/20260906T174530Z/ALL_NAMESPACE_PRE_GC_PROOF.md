# All-namespace proof — before GC

Run after reconciliation, pruning and scaffolding removal, but **before** any
reflog expiry or garbage collection. At this point the old objects were still
in the object database and would still have been found had any ref reached them.

## Reachability

```
TOTAL_REFS = 96
ALL_NAMESPACE_CARRYING_BEFORE_GC = 0
```

Method — every ref, every namespace, no curation:

```
git for-each-ref --format='%(refname)' |
while read -r ref_name; do
  if git merge-base --is-ancestor 5202bb5ffbd6b3085cdeedc68c5e9ea876a0dc96 "$ref_name" 2>/dev/null; then
    printf 'STILL_CARRYING %s\n' "$ref_name"
  fi
done
```

No output.

## Content

Armed fingerprint scanner over every blob reachable from all 96 refs, including
tags and the stash:

```
BLOBS_SCANNED                       = 5208
BLOBS_SKIPPED_OVERSIZE              = 0
ALL_NAMESPACE_SECRET_BLOBS_BEFORE_GC = 0
```

Raw output: `ALL_NAMESPACE_PRE_GC_SCAN.txt`.

This zero is admissible because the identical instrument returned **10** in the
same session, from the same object database, minutes earlier.
