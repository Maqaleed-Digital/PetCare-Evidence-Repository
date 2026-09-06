# Mirror governance — correction (append-only)

**Date:** 2026-09-06. This record corrects, and does not delete, the earlier
`DISCARDED_INVALID` classification. The earlier text remains as written; this
states what it referred to and what superseded it.

## The correction

- `DISCARDED_INVALID` referred to the **earlier, invalid** mirror at
  `tmp.ULizkXaVgX`.
- That earlier mirror **disarmed the W0-A guard** and was **destroyed**. It was
  never pushed. The prohibition on it stands.
- `~/dev/gate5-mirror.git` is the **second, post-W0-A2 mirror**. It is a
  different artefact.
- It was created **after PR #6 merged** — `filter-repo` ran 2026-09-05T12:46:42Z,
  PR #6 merged 09:44:32Z the same day.
- Its `commit-map` is keyed on `24de5399`, the post-merge `main`, which is
  exactly the starting point `GATE5_RESUME_CONDITIONS.md` required.
- `main` head-tree identity **passed** against it.
- The armed scanner showed **old > 0 and rewritten = 0** against it.
- The introducing commit was **unreachable** from its rewritten refs.
- The **Sponsor explicitly accepted** that mirror for Gate-5 publication.
- The Gate-5 Sponsor transaction used that accepted mirror, successfully.

## Why the contradiction existed

`GATE5_RESUME_CONDITIONS.md` was written while the first mirror was the only
mirror, and it says "the disposable mirror … has been discarded … the next
attempt starts from a fresh `git clone --mirror` after this PR is merged." The
second mirror **is** that fresh post-merge clone. The condemnation was read
forward onto an artefact it was never written about. The 2026-09-06
pre-authorization measurement flagged this as requiring a Sponsor ruling; the
ruling was given, and this is its record.

```
MIRROR_GOVERNANCE_CORRECTION_WRITTEN = YES
```
