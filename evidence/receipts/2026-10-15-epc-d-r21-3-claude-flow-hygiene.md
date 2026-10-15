# MVC-EPC-D-001 v1.5 — R21.3 .claude-flow hygiene lane (closes finding HYG-CLAUDE-FLOW-IGNORE)

```
UNIT=R21.3 hygiene   AUTHORITY=R21.3 (a→d), R21.2   BASE=origin/main b13016879bebf413eb69e575cc38dbd7a08cc310
EVIDENCE_DIR=evidence/replay/2026-10-15-epc-d-r21-3/ (SHA256SUMS; raw outputs sealed before interpretation)
```

## R21.3a — by-path secret scan of the two tracked logs (CLEAN; no HARD STOP)
Scanner `path_secret_scan.py` imports the repository's own `scripts/governance/secret_scan.py` PATTERNS (6:
private_key_block, aws_access_key_id, aws_secret_access_key, slack_token, github_token, google_api_key;
pattern-set sha256 bf2377688c87e94c70c601382b59df8349ed005fdfc3faf9c09b8268bfd72a48; scanner sha256 36eecae7…4cb4) and applies
them to named paths, printing pattern id and line number only — never a matched value.

| PATH (tracked on main) | BYTES / LINES | SHA256 | FINDINGS |
|---|---|---|---|
| `petcare_api/.claude-flow/policy/state.json` | 1590 / 52 | 7d6d55a2f467c21b47f56f8af5e9a8032cf99f8bb99849bff0527d6f3f8b6e82 | 0 |
| `petcare_api/tests/.claude-flow/policy/state.json` | 1590 / 52 | 4a46e01523142500c5bf7a9d796d440efb299729c90b8742e55c3b2e9a6b2466 | 0 |

Raw output `r21-3a-tracked-claude-flow-scan.out.txt` sha256 f1e95a0f736a7c81226bd9099bf2aabe0526e9c2b6b9361c718bd587445a36a6
(sealed before reading). No credential rotation is indicated by this scan.

## R21.3b — evidence bundles and manifests, before any untracking
- `verify_evidence_bundles.py`: **BUNDLES=32 ARTEFACTS=213 FAILED=0**.
- Every tracked file whose name contains `manifest` or `sha256` (363 files, all bundles included) searched for `claude-flow` and
  for each path: **0 references**. The only tracked mention of a `.claude-flow/policy/state.json` path is prose in
  `evidence/receipts/2026-10-15-epc-d-d2m-jo8-cod.md` (not a manifest). No hash edited.
- Raw output `r21-3b-bundle-and-manifest-search.out.txt` sha256 291de00f4c8719be50cb2d6698ebda66f3a9fa90d809e450e4dd41839e5dcf01.

## R21.3c — untrack and ignore (no bundle references either path)
- `git rm --cached` on both paths; both files remain on disk (1590 bytes each).
- `.gitignore`: `.claude-flow/` added with its reason.
- Tracked `.claude-flow` paths after the change: **0**. `git check-ignore` matches both paths to the new rule.
- Re-run: `verify_evidence_bundles.py` **BUNDLES=32 FAILED=0**; `secret_scan.py` **CLEAN** (`r21-3c-post-change.out.txt`).

Note: the two paths remain in published history (the repository is public). Untracking stops further publication; it does not
rewrite history, and no history rewrite is proposed — the by-path scan found nothing to withdraw.

## R21.2 — D2M stray file (confirmation; no addendum required)
The D2m receipt records that the six `secret_scan.py` PATTERNS were applied to
`evidence/replay/2026-10-15-epc-d-d2m/.claude-flow/policy/state.json` directly (1590 bytes, 52 lines; 0 findings), because the
scanner walks tracked files only. The recorded scan therefore covered the file and no addendum to the D2m receipt is written
(R21.2 requires one only if it did not). Confirming run on the retained local copy (same size and line count):
**0 findings**, file sha256 5cf8f2485afd8b7bc22463ab8c0834a0e1923c5c63232313bca08f5608d2f7bf, raw output
`r21-2-d2m-stray-scan.out.txt` sha256 46d4972fcd176cfbbe6270391080fa4a9f630fa47dbaa74bd8932774313b0464. Finding: the D2m
receipt states the method, not the exact command or a sealed output; this confirmation supplies both.

## Counts
No ledger row closes. CP1 11/19, CP2 0/40, CP3 0/20; screens 11/107; journeys 9/53; BRD FR accepted 2/31.
