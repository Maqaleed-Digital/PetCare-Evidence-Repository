#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# PH-L4 — Regulatory + Payment Validation (KSA/PDPL posture)
# Canonical executor: Claude Code (same block OK in Terminal).
# No guessing. Atomic writes. Evidence ZIP + SHA. Commit + push.
# ============================================================

REPO_ROOT="/Users/waheebmahmoud/dev/petcare-evidence-repository/petcare_execution"
cd "${REPO_ROOT}" || { echo "FATAL: missing REPO_ROOT=${REPO_ROOT}"; exit 2; }

PHASE="PETCARE-PH-L4-CLOSURE"
TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PHASE}"
OUT="${OUT_ROOT}/${TS_UTC}"
mkdir -p "${OUT}/logs" "${OUT}/snapshots"

echo "=============================================="
echo "PetCare PH-L4 CLOSURE PACK"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "=============================================="

echo ""
echo "=== STEP 0: BASELINE CHECK (NO GUESSING) ==="
need=(
  "scripts/petcare_ci_gates.sh"
  "scripts/petcare_release_integrity_check.sh"
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
echo "=== STEP 1: WRITE COMPLIANCE DOCS (tmp→mv) ==="
mkdir -p "docs" "FND" "scripts"

# docs/PDPL_COMPLIANCE.md
TMP="$(mktemp)"
cat > "${TMP}" <<'MD'
# PDPL Compliance Posture (KSA) — PetCare

**Document ID:** PETCARE-PDPL-v1
**Owner:** CEO
**Last Updated (UTC):** 2026-03-03
**Scope:** Governance + evidence repository controls and operational posture. (Product runtime controls must mirror these policies.)

## 1. Data Classification (High-level)

- **Public:** marketing content, public docs
- **Internal:** operational logs, non-sensitive governance artifacts
- **Confidential:** identifiers, customer communications, internal access logs
- **Sensitive:** health-related pet records, payment identifiers, government identifiers (if ever collected)

## 2. Core PDPL Principles Implemented

- Purpose limitation (collect only what is necessary)
- Data minimization and access control
- Retention limitation (time-bound retention + deletion)
- Integrity and confidentiality (hashes, sidecars, CI gates, controlled release)
- Auditability (evidence packs, deterministic manifests)

## 3. Access Control & Least Privilege

- GitHub branch protections and required checks enforce change control
- Release integrity checks prevent tracking secrets/env files
- Evidence artifacts are checksummed and optionally signed in higher stages

## 4. Incident Handling (PDPL-aligned)

- Follow `docs/INCIDENT_RESPONSE_PLAYBOOK.md`
- For Sev-1 security/privacy incident:
  - freeze deploy/merge
  - generate evidence pack
  - CEO notified for decision and external comms

## 5. Data Subject Rights (Operational)

Operational commitment to:
- access / correction / deletion requests (as applicable in runtime systems)
- log all requests and actions in an evidence pack for traceability

MD
chmod 0644 "${TMP}"
mv -f "${TMP}" "docs/PDPL_COMPLIANCE.md"

# docs/DATA_RETENTION_POLICY.md
TMP="$(mktemp)"
cat > "${TMP}" <<'MD'
# Data Retention Policy — PetCare

**Document ID:** PETCARE-RETENTION-v1
**Owner:** Platform Ops
**Last Updated (UTC):** 2026-03-03

## 1. Retention Categories (Baseline)

- **Governance artifacts (policies, registry, verification index):** retain indefinitely (audit required)
- **Evidence packs:** retain per operational budget (default: 30 days in CI artifacts; local evidence per ops policy)
- **Operational logs:** retain 30–90 days unless required for audit/incident
- **Production customer data (runtime systems):** subject to PDPL + business requirements (define per module)

## 2. Deletion & Disposal

- Evidence pruning uses governed tooling (no manual deletion for audited packs)
- For any deletion of audited material, create a "deletion evidence pack" with approvals

## 3. RTO/RPO Alignment

- Backup/restore capabilities validated in PH-L2
- Production RPO target must be defined once DB exists (future pack)

MD
chmod 0644 "${TMP}"
mv -f "${TMP}" "docs/DATA_RETENTION_POLICY.md"

# docs/SECURITY_BASELINE.md
TMP="$(mktemp)"
cat > "${TMP}" <<'MD'
# Security Baseline — PetCare

**Document ID:** PETCARE-SECBASE-v1
**Owner:** Platform Ops
**Last Updated (UTC):** 2026-03-03

## 1. Secrets Handling

- No secrets committed to repo (enforced by release integrity heuristic)
- No env files tracked (enforced)
- Workflows must not reference prod-like tokens (heuristic)

## 2. Change Control

- Branch protections + required checks enforced
- Policy/registry drift checks enforced
- Verification index sidecar + drift + quorum enforced

## 3. Supply Chain & Dependencies

- Lockfile determinism enforced
- pip check enforced
- compile + tests enforced in CI gates

## 4. Evidence Integrity

- Closure packs include MANIFEST + closure_sha256 + zip sha256
- Evidence size guard enforced

MD
chmod 0644 "${TMP}"
mv -f "${TMP}" "docs/SECURITY_BASELINE.md"

echo ""
echo "=== STEP 2: WRITE PAYMENT POSTURE ARTIFACT (tmp→mv) ==="
# Default posture is payments disabled unless explicitly enabled.
# This is NOT a secret; it is a governance declaration.
TMP="$(mktemp)"
cat > "${TMP}" <<'JSON'
{
  "schema": "petcare.payment_posture.v1",
  "schema_version": 1,
  "payments_enabled": false,
  "payment_provider": null,
  "notes": "PH-L4 baseline: payments disabled unless explicitly enabled via governed change."
}
JSON
chmod 0644 "${TMP}"
mv -f "${TMP}" "FND/PAYMENT_POSTURE.json"

echo ""
echo "=== STEP 3: WRITE PAYMENT POSTURE GUARD (tmp→mv) ==="
TMP="$(mktemp)"
cat > "${TMP}" <<'BASH'
#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POSTURE="${REPO_ROOT}/FND/PAYMENT_POSTURE.json"

if [ ! -f "${POSTURE}" ]; then
  echo "FATAL: missing FND/PAYMENT_POSTURE.json"
  exit 40
fi

# parse via python to avoid jq dependency
python3 - <<PY
import json,sys
p="${POSTURE}"
o=json.load(open(p,"r",encoding="utf-8"))
if o.get("schema")!="petcare.payment_posture.v1": raise SystemExit("FATAL: bad schema")
if o.get("schema_version")!=1: raise SystemExit("FATAL: bad schema_version")
pe=o.get("payments_enabled")
if pe not in (True,False): raise SystemExit("FATAL: payments_enabled must be boolean")
print("payments_enabled="+str(pe).lower())
print("payment_provider="+str(o.get("payment_provider")))
PY

PAYMENTS_ENABLED="$(python3 - <<PY
import json
o=json.load(open("${POSTURE}","r",encoding="utf-8"))
print("true" if o["payments_enabled"] else "false")
PY
)"

# Heuristic keywords that should not appear if payments are disabled.
# No guessing: keep narrow and high-signal.
PAYMENT_NEEDLES=(
  "STRIPE_"
  "TAP_"
  "HYPERPAY_"
  "PAYMENT_PROVIDER"
  "CHECKOUT_SESSION"
  "PAYMENT_INTENT"
)

if [ "${PAYMENTS_ENABLED}" = "false" ]; then
  # Fail if tracked files contain strong payment-provider configuration references.
  # Exclude docs/ because this pack introduces compliance docs that may mention the word "payment".
  for n in "${PAYMENT_NEEDLES[@]}"; do
    if git grep -n -- "${n}" -- . ":(exclude)docs" >/dev/null 2>&1; then
      echo "FATAL: payments disabled but found payment configuration reference: ${n}"
      git grep -n -- "${n}" -- . ":(exclude)docs" | head -n 20 || true
      exit 41
    fi
  done
  echo "OK: payment posture guard PASS (payments disabled; no provider refs found)"
  exit 0
fi

# payments enabled path: require provider declaration (non-secret)
python3 - <<PY
import json,sys
o=json.load(open("${POSTURE}","r",encoding="utf-8"))
if not o.get("payment_provider"):
  raise SystemExit("FATAL: payments_enabled=true requires payment_provider non-null")
print("OK: payments enabled posture has provider="+str(o["payment_provider"]))
PY

echo "OK: payment posture guard PASS (payments enabled posture valid)"
BASH
chmod +x "${TMP}"
mv -f "${TMP}" "scripts/petcare_payment_posture_guard.sh"

echo ""
echo "=== STEP 4: RUN PAYMENT POSTURE GUARD (MUST PASS) ==="
bash "scripts/petcare_payment_posture_guard.sh" | tee "${OUT}/logs/payment_posture_guard.log"

echo ""
echo "=== STEP 5: RELEASE INTEGRITY + CI GATES (MUST PASS) ==="
bash "scripts/petcare_release_integrity_check.sh" | tee "${OUT}/logs/release_integrity.log"
bash "scripts/petcare_ci_gates.sh" | tee "${OUT}/logs/ci_gates.log"

echo ""
echo "=== STEP 6: SNAPSHOT CONTROL FILES ==="
snap=(
  "docs/PDPL_COMPLIANCE.md"
  "docs/DATA_RETENTION_POLICY.md"
  "docs/SECURITY_BASELINE.md"
  "FND/PAYMENT_POSTURE.json"
  "scripts/petcare_payment_posture_guard.sh"
)
for f in "${snap[@]}"; do
  mkdir -p "${OUT}/snapshots/$(dirname "${f}")"
  cp -p "${REPO_ROOT}/${f}" "${OUT}/snapshots/${f}"
done

echo ""
echo "=== STEP 7: MANIFEST + SHA ==="
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
echo "=== STEP 8: ZIP + ZIP.SHA256 ==="
mkdir -p "${OUT_ROOT}"
ZIP="${OUT_ROOT}/${PHASE}_${TS_UTC}.zip"
rm -f "${ZIP}" "${ZIP}.sha256"
(
  cd "${OUT_ROOT}" || exit 1
  zip -r "${PHASE}_${TS_UTC}.zip" "${TS_UTC}" >/dev/null
  shasum -a 256 "${PHASE}_${TS_UTC}.zip" > "${PHASE}_${TS_UTC}.zip.sha256"
)

echo ""
echo "=== STEP 9: COMMIT / PUSH ==="
git status -sb | tee "${OUT}/logs/git_status.log"

git add \
  "docs/PDPL_COMPLIANCE.md" \
  "docs/DATA_RETENTION_POLICY.md" \
  "docs/SECURITY_BASELINE.md" \
  "FND/PAYMENT_POSTURE.json" \
  "scripts/petcare_payment_posture_guard.sh"

git commit -m "PH-L4: PDPL posture + payment posture guard"
git push origin main

echo ""
echo "DONE"
echo "ZIP=${ZIP}"
echo "ZIP_SHA=${ZIP}.sha256"
echo "COMMIT=$(git rev-parse HEAD)"
