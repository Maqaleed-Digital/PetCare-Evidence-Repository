# CI gap remediation — an empty check set is not a pass

**Date:** 2026-09-04 · **Under:** `MVC-GOV-CANON-001`

## The defect

PR #3 merged into `main` with `statusCheckRollup = []`, and the run that merged
it recorded CI as green. Nothing was green. Nothing had run.

```
PR3_EMPTY_ROLLUP_WAS_NOT_CI_SUCCESS = YES
```

Three things had to be true at once, and all three were.

**1. Neither root workflow can produce a pull-request check.**
`.github/workflows/verification-index-gate-final.yml` and
`release-policy-auto.yml` both trigger only on `release: published` (the first
also on `workflow_dispatch`). Correct for what they do — release gating — and
structurally unable to gate a pull request.

**2. The workflow that does trigger on pull requests is in the wrong place.**
`petcare_execution/.github/workflows/ci.yml` triggers on `push` and
`pull_request`. It has never run once: GitHub Actions reads only the
repository-root `.github/workflows`. A **nested** `.github` directory is inert.

The repository therefore carried **three workflow files and zero pull-request
checks**. Counting workflow files is what made it look covered.

**3. The predicate was wrong.** "No check failed" is satisfied perfectly by an
empty set. It cannot distinguish *passed* from *never attempted* — the same
defect as a pytest run that exits 0 having collected nothing.

## The remediation

| Artefact | What it does |
|---|---|
| `.github/workflows/verify.yml` | Root workflow, job id **`verify`**, triggers on `pull_request` and on pushes to `main`, `govern/**`, `security/**`, `wave0/**`. Runs the acceptance surface PORT-01..10 already proved. No secrets. |
| `scripts/governance/ci_verdict.py` | Fail-closed verdict: **PASS** requires at least one required check present *and* every required check successful. Absent → `NOT_PROVEN`, never PASS. |
| `tests/governance/test_ci_verification_contract.py` | 15 cases pinning both halves. |
| `scripts/governance/secret_scan.py` | Tracked-files scanner with a reasoned allowlist. |
| `scripts/governance/prohibited_literal_scan.py` | Anchored active-default detector. |
| `scripts/governance/verify_evidence_bundles.py` | Verifies both evidence manifest schemes. |
| `tests/governance/test_repository_scanners.py` | 11 cases driving each scanner against synthetic positives and lookalikes. |

```
CI_WORKFLOW_IN_REPOSITORY = YES  (.github/workflows/verify.yml)
CI_PRIMARY_CHECK_NAME     = verify
```

### Verdict semantics, proven three ways

| Rollup | Verdict |
|---|---|
| `[]` — the PR #3 condition | **NOT_PROVEN** |
| `verify: success` | PASS |
| `verify: failure` | FAIL |
| `verify: skipped / neutral / cancelled / stale / ""` | not PASS |
| green checks that do not include `verify` | **NOT_PROVEN** |
| a verdict over an empty *requirement* set | raises — the same vacuity one level up |

## Three defects the remediation itself produced, and how they were caught

Each was caught by a guard written alongside it, which is the argument for
scripts over shell one-liners: a script can be unit-tested against a known-bad
input; a `grep` buried in YAML cannot.

**The secret scan matched its own regex.** The first version was a shell
`grep -rE` for key patterns. It found two files: the workflow step containing
the pattern, and an older release-integrity script carrying an equivalent one.
It would have failed CI on a repository containing no secrets — the kind of
failure that trains people to ignore the check.

**The allowlist was already carrying dead weight.** Two of the three initial
entries matched nothing: this scanner's own patterns use character classes
(`[A-Z ]*`, `[0-9A-Z]{16}`) and so do not match themselves, and the workflow
only names the scripts. A test now asserts every entry *would* have been a
finding without it. Allowlisting "just in case" creates a permanent blind spot
over a file nobody re-reads.

**The scanner's own test file was a finding.** The synthetic positive for the
private-key pattern was written as a literal header, which the scanner correctly
flagged the moment the file was staged. The tempting fix — allowlist the test
file — would have blinded the scanner to the one place a real secret is most
likely to be pasted while debugging. Every sample is now assembled from
fragments instead.

## The evidence step, and a scheme that was not obvious

`sha256sum -c EVIDENCE_SHA256.txt` fails on half the bundles here, and its error
is "No such file or directory" — which reads as missing evidence and is not.
Two schemes exist:

- **A** — per-file `<sha256>  <filename>` lines. 3 bundles.
- **B** — one line whose "filename" is the bundle id; per-artefact hashes live
  in `MANIFEST.json` beside a `bundle_sha256` aggregate. 3 bundles.

Both are verified. **6 bundles, 31 artefacts, 0 mismatches.**

What is deliberately *not* claimed: `bundle_sha256`'s derivation from the
artefact hashes could not be reproduced — seven candidate constructions were
tried and none matched — so it is checked only for internal consistency against
the `EVIDENCE_SHA256.txt` line and reported as `UNDERIVED`. Guessing until
something matched would have manufactured an integrity check that proves
nothing.

## What this run did not do, and why

```
BRANCH_PROTECTION_REQUIRED_CHECK_ENABLED = NO
```

Measured read-only: `main` returns **"Branch not protected" (404)** and the
repository has **zero rulesets**. Making `verify` a required check is external
GitHub configuration — **GATE-3** — and was not performed.

Until it is, `verify` runs on pull requests and reports, but nothing stops a
merge that ignores it. The repository half of the defect is closed; the
enforcement half is a Sponsor action.
