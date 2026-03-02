#!/usr/bin/env bash
set -euo pipefail

PHASE="PETCARE-PH62-CLOSURE"
TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PHASE}"
OUT="${OUT_ROOT}/${TS_UTC}"

mkdir -p "${OUT}/logs" "${OUT}/fixtures" "${OUT}/snapshots"

echo "=============================================="
echo "PetCare PH62 CLOSURE PACK"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "=============================================="

need=(
  "FND/VERIFICATION_POLICY.json"
  "FND/VERIFICATION_POLICY.sha256"
  "FND/VERIFICATION_POLICY_CHANGELOG.md"
  "FND/VERIFICATION_INDEX.json"
  "scripts/petcare_verification_policy_verify.py"
  "scripts/petcare_verification_policy_changelog_add.py"
  "scripts/petcare_verification_index_verify.py"
  "scripts/petcare_ci_gates.sh"
)
missing=0
for f in "${need[@]}"; do
  if [ ! -f "${REPO_ROOT}/${f}" ]; then
    echo "MISSING_REQUIRED_FILE=${f}" | tee -a "${OUT}/logs/missing_files.log"
    missing=1
  fi
done
if [ "${missing}" -ne 0 ]; then
  echo "FATAL: missing required files. Stop (no guessing)."
  exit 3
fi

echo ""
echo "=== STEP 1: POLICY VERIFY ==="
python3 "${REPO_ROOT}/scripts/petcare_verification_policy_verify.py" \
  | tee "${OUT}/logs/policy_verify.log"

echo ""
echo "=== STEP 2: REAL INDEX VERIFY (STRICT ON) ==="
set +e
python3 "${REPO_ROOT}/scripts/petcare_verification_index_verify.py" \
  --index "${REPO_ROOT}/FND/VERIFICATION_INDEX.json" \
  | tee "${OUT}/logs/index_verify_real.log"
rc_real=${PIPESTATUS[0]}
set -e
echo "REAL_INDEX_VERIFY_RC=${rc_real}" | tee -a "${OUT}/logs/index_verify_real.log"
# Expected: either 0 (quorum met) or 135 (quorum not met). Any other is failure.
if [ "${rc_real}" -ne 0 ] && [ "${rc_real}" -ne 135 ]; then
  echo "FATAL: unexpected rc=${rc_real} from real index verify." | tee -a "${OUT}/logs/index_verify_real.log"
  exit 10
fi

echo ""
echo "=== STEP 3: FIXTURE INTEGRITY FAIL (DUP ID) — EXPECT rc=34 ==="
cat > "${OUT}/fixtures/index_integrity_fail_dup_id.json" <<'JSON'
[
  {"entry_id":"dup","verifier_pack":"PETCARE-PH44B-CLOSURE"},
  {"entry_id":"dup","verifier_pack":"PETCARE-PH45B-CLOSURE"}
]
JSON

set +e
python3 "${REPO_ROOT}/scripts/petcare_verification_index_verify.py" \
  --index "${OUT}/fixtures/index_integrity_fail_dup_id.json" \
  | tee "${OUT}/logs/index_verify_fixture_integrity_fail.log"
rc_ifail=${PIPESTATUS[0]}
set -e
echo "INTEGRITY_FAIL_RC=${rc_ifail}" | tee -a "${OUT}/logs/index_verify_fixture_integrity_fail.log"
if [ "${rc_ifail}" -ne 34 ]; then
  echo "FATAL: expected rc=34 for integrity fail, got rc=${rc_ifail}" | tee -a "${OUT}/logs/index_verify_fixture_integrity_fail.log"
  exit 11
fi

echo ""
echo "=== STEP 4: FIXTURE QUORUM FAIL (SINGLE META) — EXPECT rc=135 ==="
cat > "${OUT}/fixtures/index_quorum_fail.json" <<'JSON'
[
  {"entry_id":"a","verifier_pack":"PETCARE-PH44B-CLOSURE"},
  {"entry_id":"b","verifier_pack":"PETCARE-PH44B-CLOSURE"}
]
JSON

set +e
python3 "${REPO_ROOT}/scripts/petcare_verification_index_verify.py" \
  --index "${OUT}/fixtures/index_quorum_fail.json" \
  | tee "${OUT}/logs/index_verify_fixture_quorum_fail.log"
rc_qfail=${PIPESTATUS[0]}
set -e
echo "QUORUM_FAIL_RC=${rc_qfail}" | tee -a "${OUT}/logs/index_verify_fixture_quorum_fail.log"
if [ "${rc_qfail}" -ne 135 ]; then
  echo "FATAL: expected rc=135 for quorum fail, got rc=${rc_qfail}" | tee -a "${OUT}/logs/index_verify_fixture_quorum_fail.log"
  exit 12
fi

echo ""
echo "=== STEP 5: FIXTURE QUORUM PASS (TWO DISTINCT META) — EXPECT rc=0 ==="
cat > "${OUT}/fixtures/index_quorum_pass.json" <<'JSON'
[
  {"entry_id":"a","verifier_pack":"PETCARE-PH44B-CLOSURE"},
  {"entry_id":"b","verifier_pack":"PETCARE-PH45B-CLOSURE"}
]
JSON

python3 "${REPO_ROOT}/scripts/petcare_verification_index_verify.py" \
  --index "${OUT}/fixtures/index_quorum_pass.json" \
  | tee "${OUT}/logs/index_verify_fixture_quorum_pass.log"

echo ""
echo "=== STEP 6: CHANGELOG APPEND (RECORD POLICY SHA) ==="
python3 "${REPO_ROOT}/scripts/petcare_verification_policy_changelog_add.py" \
  --pack "PH62-RESTORE-INDEX-INTEGRITY(strict=on)" \
  --ts "${TS_UTC}" \
  | tee "${OUT}/logs/changelog_add.log"

echo ""
echo "=== STEP 7: CI GATES ==="
bash "${REPO_ROOT}/scripts/petcare_ci_gates.sh" \
  | tee "${OUT}/logs/ci_gates.log"

echo ""
echo "=== SNAPSHOT CONTROL FILES ==="
snap=(
  "FND/VERIFICATION_POLICY.json"
  "FND/VERIFICATION_POLICY.sha256"
  "FND/VERIFICATION_POLICY_CHANGELOG.md"
  "FND/VERIFICATION_INDEX.json"
  "scripts/petcare_verification_index_verify.py"
  "scripts/petcare_ph62_closure_pack.sh"
)
for f in "${snap[@]}"; do
  mkdir -p "${OUT}/snapshots/$(dirname "${f}")"
  cp -p "${REPO_ROOT}/${f}" "${OUT}/snapshots/${f}"
done

echo ""
echo "=== MANIFEST ==="
python3 - <<PY
import json
from pathlib import Path
out=Path("${OUT}")
files=[str(p.relative_to(out)) for p in sorted(out.rglob("*")) if p.is_file()]
m={"phase":"${PHASE}","timestamp_utc":"${TS_UTC}","file_count":len(files),"files":files}
(out/"MANIFEST.json").write_text(json.dumps(m, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
print("OK wrote MANIFEST.json")
PY

echo ""
echo "=== SHA256 (SORTED) ==="
(
  cd "${OUT}" || exit 1
  find . -type f -print0 \
  | LC_ALL=C sort -z \
  | xargs -0 shasum -a 256 \
  > "closure_sha256.txt"
)

echo ""
echo "=== ZIP + ZIP.SHA256 ==="
mkdir -p "${OUT_ROOT}"
ZIP="${OUT_ROOT}/${PHASE}_${TS_UTC}.zip"
rm -f "${ZIP}" "${ZIP}.sha256"
(
  cd "${OUT_ROOT}" || exit 1
  zip -r "${PHASE}_${TS_UTC}.zip" "${TS_UTC}" >/dev/null
  shasum -a 256 "${PHASE}_${TS_UTC}.zip" > "${PHASE}_${TS_UTC}.zip.sha256"
)

echo ""
echo "DONE"
echo "OUT=${OUT}"
echo "ZIP=${ZIP}"
