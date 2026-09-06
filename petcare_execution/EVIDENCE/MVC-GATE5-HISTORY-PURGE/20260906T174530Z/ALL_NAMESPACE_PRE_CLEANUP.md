# All-namespace pre-cleanup sweep

Every ref in every namespace was tested for reachability of the introducing
commit. This is deliberately **not** a curated `refs/heads`-only acceptance: the
Gate-5 scaffolding lived in `refs/remotes/gate5probe`, `refs/remotes/gate5mirror`
and `refs/gate5new`, and a heads-only sweep would have declared the repository
clean while 42 probe refs still carried the literal.

```
TOTAL_REFS_AT_SWEEP = 241
ALL_NAMESPACE_PRE_CLEANUP_CARRYING = 20
```

## The 20 carrying refs, enumerated

**Local heads (14)**

```
refs/heads/gate-evidence-prep
refs/heads/govern/canonical-repository-authority
refs/heads/govern/denominator-inventory
refs/heads/m8-brand-cleanup
refs/heads/main
refs/heads/mvc-ux-wo-001
refs/heads/mvc-ux-wo-002-trust-surfaces
refs/heads/security/w0a-require-session-signing-key
refs/heads/security/w0a2-fingerprint-guard
refs/heads/wave0/w0-a-remove-hardcoded-secret-fallback
refs/heads/wave0/w0-b-session-bound-authorization
refs/heads/wave0/w0-c-server-derived-tenant
refs/heads/wave0/w0-d-dispensing-fail-closed
refs/heads/wave0/w0-e-withdraw-unsupported-attestation
```

**Probe remote-tracking refs (6)**

```
refs/remotes/gate5probe/gate-evidence-prep
refs/remotes/gate5probe/m8-brand-cleanup
refs/remotes/gate5probe/main
refs/remotes/gate5probe/mvc-ux-wo-001
refs/remotes/gate5probe/mvc-ux-wo-002-trust-surfaces
refs/remotes/gate5probe/security/w0a-require-session-signing-key
```

The 14 local heads reproduce the T0 count exactly.

## Namespaces that were already clean

```
refs/remotes/origin/*     43 refs — 0 carrying
refs/gate5new/*           50 refs — 0 carrying (these are the rewritten targets)
refs/remotes/gate5mirror/* 50 refs — 0 carrying (rewritten mirror)
refs/tags/*                7 tags — 0 carrying
refs/stash                 1 ref  — 0 carrying
```

These 20 refs were the retained old history. They are what made the positive
control in `OLD_HISTORY_POSITIVE_CONTROL.md` possible, and they were kept in
place until that control had passed and been sealed.
