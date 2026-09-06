# Gate-5 scaffolding cleanup

Removed **only after** the positive control had run and been sealed
(`OLD_HISTORY_POSITIVE_CONTROL.md`). These namespaces held the old objects that
made the control possible.

```
GATE5PROBE_REFS_REMOVED  = 42
GATE5MIRROR_REFS_REMOVED = 50
GATE5NEW_REFS_REMOVED    = 50
GATE5MIRROR_REMOTE_REMOVED = YES
```

All three counts reproduce the frozen T0 figures exactly.

Method:

```
git for-each-ref --format='delete %(refname)' <namespace> | git update-ref --stdin
git remote remove gate5mirror
```

After removal each namespace enumerates to zero refs.

## Deliberately not removed

```
origin        retained (the only remaining remote)
refs/stash    retained
refs/tags/*   retained (7)
refs/heads/*  retained except the 3 measured prunes
```

`refs/gate5new/*` was the local cross-check for the commit-map. It was consumed
before removal: every mapping used in this closeout was confirmed against it,
and the durable artefact — `FILTER_REPO_COMMIT_MAP.txt` — is preserved in this
pack, so the mapping remains auditable after the refs are gone.
