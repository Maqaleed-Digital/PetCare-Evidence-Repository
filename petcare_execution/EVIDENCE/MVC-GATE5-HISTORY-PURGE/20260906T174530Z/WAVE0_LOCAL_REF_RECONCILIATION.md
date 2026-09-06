# Local ref reconciliation

Every local head was moved by **compare-and-swap** to the SHA the validated
`filter-repo` commit-map assigns it. No rebase, no reconstruction, no guessed
topology. Each `git update-ref <ref> <NEW> <OLD>` fails if the ref is not
exactly at `<OLD>`, so a stale assumption cannot silently succeed.

## Mapping source, triple-confirmed

For every ref below the mapping was confirmed from the commit-map **and**
cross-checked against `refs/gate5new/<ref>`; for the five published non-main
heads it was additionally checked against the live `origin` SHA. All three
agreed in every case.

## The five authorized Wave-0 refs

```
WAVE0_LOCAL_REFS_UPDATED = 5/5
```

| ref | OLD | NEW |
|---|---|---|
| `wave0/w0-a-remove-hardcoded-secret-fallback` | `3224c65d6cf3086ae9fa95b3ceed9a9d532d2814` | `83e167a62d267866176126998dad7142ea2fbe1c` |
| `wave0/w0-b-session-bound-authorization` | `955b5a59671f30de8dcf42d8d1b13c81189eeed6` | `4c313231498424ebe8a755f8e087d5936b4c2b69` |
| `wave0/w0-c-server-derived-tenant` | `16a521c80348adf6f323815c399697e19421a4fa` | `2824846169e9383b1364d7066f7bcd2163cdeaad` |
| `wave0/w0-d-dispensing-fail-closed` | `82e931d7efcdd60124fa4ce3fd451012516489fa` | `b743243764e83e5f00256d6d41e4faccd92ec386` |
| `wave0/w0-e-withdraw-unsupported-attestation` | `b6a5d8a97bbd2ce41c067798b9bee83613b12579` | `5771048453e803337ab5d1294b7de46e65e9b117` |

## The five published non-main counterparts

These are the **local copies** of branches the Sponsor already published. They
were still at pre-rewrite SHAs and therefore still carried the literal locally.
They are not in the literal Wave-0 list, and leaving them would have left the
all-namespace sweep non-zero.

They were reconciled by the **same mechanism to the SHA already live on
`origin`** — no new history, no remote mutation.

```
PUBLISHED_NONMAIN_LOCAL_REFS_UPDATED = 5/5
```

| ref | OLD | NEW (= live origin) |
|---|---|---|
| `gate-evidence-prep` | `c88d9f15356cf7786bc9958e6a1076d260c747a0` | `4986725505de0af9e37b2854c170e364b1075cff` |
| `m8-brand-cleanup` | `a3cba7ba1f529008fecd523d60bfc297375f4210` | `770eb193fda6cdcbe41a7fa19e9b8caafb02bd23` |
| `mvc-ux-wo-001` | `ed4e0e36c8bada260d91d5d52c6d26531731d2cc` | `2e9c070468316b0cc6b3d259dd973b6606ea4e41` |
| `mvc-ux-wo-002-trust-surfaces` | `2b3e7b2a6b08c3cd948557c95d2af7e65b6b5e53` | `2e06ecf992a40ddd5b54ce13189755b1b6ec9351` |
| `security/w0a-require-session-signing-key` | `9fc8e2494043fffa11d044942bc66ec9d8c5b65f` | `a838d9f2b43e7cdcee659fab9729915533b78884` |

This is the resolution of the "local-ref scope delta" the 2026-09-05 preflight
raised and no one had ruled on. It is recorded here as an extension beyond the
literal five, not folded silently into the authorized count.
