#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# PH-L3 — Ops Runbook + Incident Response + Rollback Drill
# ============================================================

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

PHASE="PETCARE-PH-L3-CLOSURE"
TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PHASE}"
OUT="${OUT_ROOT}/${TS_UTC}"
mkdir -p "${OUT}/logs" "${OUT}/snapshots"

echo "=============================================="
echo "PetCare PH-L3 CLOSURE PACK"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "=============================================="

echo ""
echo "=== STEP 0: BASELINE CHECK (NO GUESSING) ==="
need=(
  "scripts/petcare_ci_gates.sh"
  "scripts/petcare_release_integrity_check.sh"
  "scripts/petcare_verification_index_verify.py"
  "FND/VERIFICATION_INDEX.json"
  "FND/VERIFICATION_INDEX.sha256"
)
missing=0
for f in "${need[@]}"; do
  if [ ! -f "${f}" ]; then echo "MISSING_REQUIRED_FILE=${f}"; missing=1; fi
done
if [ "${missing}" -ne 0 ]; then
  echo "FATAL: missing required files. Stop (no guessing)."
  exit 3
fi

echo ""
echo "=== STEP 1: WRITE OPS DOCS (tmp→mv) ==="
mkdir -p "docs"

TMP="$(mktemp)"
cat > "${TMP}" <<'MD'
# PetCare Production Runbook

**Document ID:** PETCARE-RUNBOOK-PROD-v1
**Owner:** Waheeb Ghassan Mahmoud (CEO)
**Maintainer:** Platform Ops
**Last Updated (UTC):** 2026-03-03
**Scope:** PetCare Evidence Repository governance runtime, CI gating, verification index/policy integrity.

## 1. Production Principles

- **No guessing:** If a required artifact is missing, stop and escalate.
- **Determinism:** Regenerate artifacts only through governed tooling.
- **Evidence-first:** Every intervention produces an evidence pack.
- **Rollback-first:** Prefer reverting to last known-good tag/commit over ad-hoc patching.

## 2. Production Baseline

Required invariants before any production action:

- `bash scripts/petcare_ci_gates.sh` → PASS
- `bash scripts/petcare_release_integrity_check.sh` → PASS
- Verification index sidecar + drift + quorum gates → enforced via CI

## 3. Roles & On-Call Escalation

### Escalation Matrix

| Severity | Owner | Backup | Notify |
|---|---|---|---|
| Sev-1 | Platform Ops Lead | CEO | All stakeholders |
| Sev-2 | Platform Ops Lead | Eng Lead | Key stakeholders |
| Sev-3 | Eng On-call | Platform Ops Lead | Internal only |

### Communication Channels

- Internal: (define) Slack/WhatsApp group + GitHub issue thread
- External: (define) customer notification channel (email/SMS/app banner)

## 4. Standard Operating Procedures

### 4.1 Health & Integrity Check (baseline)

Run from repo root:

- `bash scripts/petcare_release_integrity_check.sh`
- `bash scripts/petcare_ci_gates.sh`

Expected: PASS.

### 4.2 Evidence Pack Procedure (every intervention)

- Create closure pack evidence under `evidence_output/<PHASE>/`
- Ensure ZIP + `.sha256` exist
- Record commit hash and tag if applicable

## 5. Backup/Restore Reference

- PH-L2 provides `scripts/petcare_backup_create.sh` and `scripts/petcare_restore_apply.sh`
- Target RTO budget is enforced by PH-L2 closure pack.

## 6. Rollback Procedure (tabletop + operational)

### Trigger Conditions

- CI gates fail after merge to main
- Verification index quorum/integrity fails
- Release integrity check fails
- Production incident requiring immediate restoration of known-good state

### Steps (Operational)

1) Identify last known-good release tag (example pattern): `petcare-prod-YYYYMMDD.N`
2) Verify repo clean: `git status -sb`
3) Re-run CI gates on the tag:
   - `git checkout <TAG>`
   - `bash scripts/petcare_ci_gates.sh`
4) Restore main:
   - `git checkout main`

### Evidence Required

- Tag selected
- CI gates output on tag
- Decision log (why rollback, who approved)

## 7. Approvals & Sign-off

- **CEO Sign-off required** for: Sev-1 incident close, production rollback, public launch enablement.
MD
chmod 0644 "${TMP}"
mv -f "${TMP}" "docs/PRODUCTION_RUNBOOK.md"

TMP="$(mktemp)"
cat > "${TMP}" <<'MD'
# PetCare Incident Response Playbook

**Document ID:** PETCARE-IRP-v1
**Owner:** Platform Ops
**Last Updated (UTC):** 2026-03-03

## 1. Severity Definitions

- **Sev-1:** Production down, data integrity risk, security incident, or loss of quorum/integrity in verification index affecting release governance.
- **Sev-2:** Partial outage, degraded performance, failed deployment with quick mitigation, non-critical integrity warnings.
- **Sev-3:** Minor bug, cosmetic issue, non-blocking CI issue in non-release context.

## 2. Triage Workflow

1) **Detect:** monitoring/CI alert/user report
2) **Stabilize:** stop the bleeding (freeze deploys, block merges if needed)
3) **Validate integrity:** run release integrity + CI gates
4) **Mitigate:** rollback or hotfix (rollback preferred)
5) **Recover:** restore services, confirm integrity and quorum
6) **Postmortem:** evidence pack + corrective actions

## 3. First 15 Minutes Checklist (Sev-1)

- Announce incident internally (time started, impact)
- Freeze changes: no merges, no deploys
- Run:
  - `bash scripts/petcare_release_integrity_check.sh`
  - `bash scripts/petcare_ci_gates.sh`
- Capture outputs into an evidence pack
- Decide rollback vs fix (rollback preferred)
- Notify CEO for approval

## 4. Communications Templates

### Internal update
- Start time (UTC):
- Impact:
- Current status:
- Next update time:

### External update
- We are experiencing a service disruption.
- Status: investigating / mitigating / recovered.
- Next update time.

## 5. Post-Incident Requirements

- Root cause summary
- Evidence ZIP path + sha256
- Remediation tasks (with owners + deadlines)
- "What would have prevented this?" section
MD
chmod 0644 "${TMP}"
mv -f "${TMP}" "docs/INCIDENT_RESPONSE_PLAYBOOK.md"

echo ""
echo "=== STEP 2: WRITE GUARD scripts/petcare_ops_runbook_guard.sh (tmp→mv) ==="
TMP="$(mktemp)"
cat > "${TMP}" <<'BASH'
#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

req_files=(
  "docs/PRODUCTION_RUNBOOK.md"
  "docs/INCIDENT_RESPONSE_PLAYBOOK.md"
)

for f in "${req_files[@]}"; do
  if [ ! -f "${REPO_ROOT}/${f}" ]; then
    echo "FATAL: missing required doc: ${f}"
    exit 3
  fi
done

must_have_prod=(
  "^# PetCare Production Runbook"
  "^\*\*Document ID:\*\*"
  "^## 3\. Roles & On-Call Escalation"
  "^## 6\. Rollback Procedure"
)

must_have_irp=(
  "^# PetCare Incident Response Playbook"
  "^\*\*Document ID:\*\*"
  "^## 1\. Severity Definitions"
  "^## 3\. First 15 Minutes Checklist"
  "^## 4\. Communications Templates"
)

for pat in "${must_have_prod[@]}"; do
  if ! grep -qE "${pat}" "${REPO_ROOT}/docs/PRODUCTION_RUNBOOK.md"; then
    echo "FATAL: PRODUCTION_RUNBOOK missing pattern: ${pat}"
    exit 31
  fi
done

for pat in "${must_have_irp[@]}"; do
  if ! grep -qE "${pat}" "${REPO_ROOT}/docs/INCIDENT_RESPONSE_PLAYBOOK.md"; then
    echo "FATAL: INCIDENT_RESPONSE_PLAYBOOK missing pattern: ${pat}"
    exit 32
  fi
done

echo "OK: PH-L3 runbook guard PASS"
BASH
chmod +x "${TMP}"
mv -f "${TMP}" "scripts/petcare_ops_runbook_guard.sh"

echo ""
echo "=== STEP 3: RUNBOOK GUARD (MUST PASS) ==="
bash "scripts/petcare_ops_runbook_guard.sh" | tee "${OUT}/logs/runbook_guard.log"

echo ""
echo "=== STEP 4: TABLETOP DRILLS (DETERMINISTIC LOGS) ==="
echo "ts_utc=${TS_UTC}" | tee "${OUT}/logs/drill_context.log"
echo "repo_root=${REPO_ROOT}" | tee -a "${OUT}/logs/drill_context.log"

# 4.1 Integrity baseline capture
bash "scripts/petcare_release_integrity_check.sh" | tee "${OUT}/logs/drill_release_integrity.log"
bash "scripts/petcare_ci_gates.sh" | tee "${OUT}/logs/drill_ci_gates.log"

# 4.2 Verification index verify
python3 "scripts/petcare_verification_index_verify.py" \
  --index "${REPO_ROOT}/FND/VERIFICATION_INDEX.json" \
  | tee "${OUT}/logs/drill_index_verify.log"

# 4.3 Rollback rehearsal (safe): checkout last prod tag, run CI gates, return to main
LAST_PROD_TAG="$(git tag --list 'petcare-prod-*' | LC_ALL=C sort | tail -n 1 || true)"
echo "last_prod_tag=${LAST_PROD_TAG:-NONE}" | tee "${OUT}/logs/drill_rollback.log"

if [ -n "${LAST_PROD_TAG}" ]; then
  CUR_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
  echo "current_branch=${CUR_BRANCH}" | tee -a "${OUT}/logs/drill_rollback.log"

  git status -sb | tee -a "${OUT}/logs/drill_rollback.log"

  echo "checkout_tag=${LAST_PROD_TAG}" | tee -a "${OUT}/logs/drill_rollback.log"
  git checkout -q "${LAST_PROD_TAG}"

  echo "run_ci_on_tag" | tee -a "${OUT}/logs/drill_rollback.log"
  bash "scripts/petcare_ci_gates.sh" | tee "${OUT}/logs/drill_ci_on_tag.log"

  echo "return_to_branch=${CUR_BRANCH}" | tee -a "${OUT}/logs/drill_rollback.log"
  git checkout -q "${CUR_BRANCH}"
else
  echo "SKIP: no prod tag found (pattern petcare-prod-*). No guessing." | tee -a "${OUT}/logs/drill_rollback.log"
fi

echo ""
echo "=== STEP 5: SNAPSHOT CONTROL FILES ==="
snap=(
  "docs/PRODUCTION_RUNBOOK.md"
  "docs/INCIDENT_RESPONSE_PLAYBOOK.md"
  "scripts/petcare_ops_runbook_guard.sh"
)
for f in "${snap[@]}"; do
  mkdir -p "${OUT}/snapshots/$(dirname "${f}")"
  cp -p "${REPO_ROOT}/${f}" "${OUT}/snapshots/${f}"
done

echo ""
echo "=== STEP 6: MANIFEST + SHA ==="
python3 - <<PY
import json
from pathlib import Path
out=Path("${OUT}")
files=[str(p.relative_to(out)) for p in sorted(out.rglob("*")) if p.is_file()]
m={"phase":"${PHASE}","timestamp_utc":"${TS_UTC}","file_count":len(files),"files":files}
(out/"MANIFEST.json").write_text(json.dumps(m, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
print("OK wrote MANIFEST.json")
PY

(
  cd "${OUT}" || exit 1
  find . -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 > "closure_sha256.txt"
)

echo ""
echo "=== STEP 7: ZIP + ZIP.SHA256 ==="
mkdir -p "${OUT_ROOT}"
ZIP="${OUT_ROOT}/${PHASE}_${TS_UTC}.zip"
rm -f "${ZIP}" "${ZIP}.sha256"
(
  cd "${OUT_ROOT}" || exit 1
  zip -r "${PHASE}_${TS_UTC}.zip" "${TS_UTC}" >/dev/null
  shasum -a 256 "${PHASE}_${TS_UTC}.zip" > "${PHASE}_${TS_UTC}.zip.sha256"
)

echo ""
echo "=== STEP 8: COMMIT / PUSH ==="
git status -sb | tee "${OUT}/logs/git_status.log"

git add \
  "docs/PRODUCTION_RUNBOOK.md" \
  "docs/INCIDENT_RESPONSE_PLAYBOOK.md" \
  "scripts/petcare_ops_runbook_guard.sh"

git commit -m "PH-L3: ops runbook + incident playbook + rollback drill evidence"
git push origin main

echo ""
echo "DONE"
echo "ZIP=${ZIP}"
echo "ZIP_SHA=${ZIP}.sha256"
echo "COMMIT=$(git rev-parse HEAD)"
