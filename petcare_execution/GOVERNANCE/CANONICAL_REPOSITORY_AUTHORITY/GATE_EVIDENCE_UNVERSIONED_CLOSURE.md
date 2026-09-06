# GATE_EVIDENCE_UNVERSIONED — closure record

**Gate:** `GATE_EVIDENCE_UNVERSIONED`
**Authority:** `MVC-GOV-CANON-001`
**Closed:** 2026-09-03
**Custody commit:** `66ec0c32c1d5b15d9bd6eccce55728b17d1b79c5`
**Hash-binding commit:** `25dbcea4e7077cfee1d4065f400b40c5b528c963`

## The defect

Forty gate-evidence files existed on local disk. Zero were tracked by git — in
this repository or in `petcare-platform`. Twenty citations, from twenty
`CLOSED_EVIDENCED` requirements across fourteen distinct paths, pointed at them.
The evidence underwriting those closures was protected by one working copy.

## Why it was untracked

`UNTRACKED_BY_OMISSION`, not policy. `git check-ignore` matches nothing under
`evidence/` — neither the directory nor any representative file. `.gitignore`
ignores `petcare_execution/evidence_output/`, which is a different path. Nobody
had run `git add`.

## The custody chain, proven end to end

| Step | Result |
|---|---|
| Files on disk (re-measured, not assumed) | 40 |
| Files tracked before | 0 |
| Pre-commit hash seal | 40 hashes, seal `b8b55dc6…` |
| Secret adjudication (before history mutation) | `CLEARED_FOR_CUSTODY` |
| Byte-preserving policy | `.gitattributes` → `evidence/** -text`; evidence reports `text: unset`, other files stay `unspecified` |
| Index byte equality (`git show :path` vs worktree) | 40 files, **0 mismatches** |
| Clean detached-worktree checkout vs pre-seal | **zero differences** |
| Files tracked after | **40** |
| Cited paths hash-bound | **14 / 14** (10 files, 4 directory manifests) |
| Standing guard armed | **YES** — proven failing on a controlled negative fixture |

`INDEX_BYTES_PRESERVED=YES` · `CLEAN_CHECKOUT_BYTES_PRESERVED=YES` ·
`CITATIONS_REMAINING_UNBOUND=0` · `CUSTODY_GUARD_ARMED=YES`

## Judgements worth recording

**`git diff --cached --check` was not obeyed, deliberately.** It reported 46
trailing-whitespace lines across five evidence files. That whitespace *is* the
evidence: pytest emits trailing spaces on `DeprecationWarning` lines, and three
Markdown artefacts use the two-space hard line break. `--check` is a lint for
source about to be written, not for bytes being preserved by hash. Stripping it
would have defeated the only purpose of the custody commit.

**Directory citations get manifest hashes.** Four of the fourteen cited paths
are directories. A directory has no file hash, so each is hashed over its
members' sorted `relpath  sha256` lines — re-derivable, and sensitive to any
member changing.

**The hashes are retrospective and say so.** They were bound on 2026-09-03 and
did not exist at the original closure dates. The index records
`hash_binding_date` separately, no original closure date was altered, and a
standing test asserts the index keeps admitting this. A hash that implied it had
always been present would be a worse artefact than no hash at all.

**The count is 20 citations, not 104.** 104 is the number of `CLOSED_EVIDENCED`
requirements; only 20 of them carry `evidence_paths`. The other 84 are evidenced
by code and tests alone and cite no gate artefact.

## Standing guard

`petcare-platform/tests/test_phase16_governance_integrity.py` now asserts, for
every evidenced citation: the path exists, it is tracked by git in the canonical
repository, a bound hash exists, the bytes still produce it, no citation falls
outside custody, and the binding still declares itself retrospective. A vacuity
guard proves the assertion set is non-empty.

`GATE_STATUS=CLOSED`
