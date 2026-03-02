#!/usr/bin/env bash
set -euo pipefail

PHASE="PETCARE-PH61-CLOSURE"
TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PHASE}"
OUT="${OUT_ROOT}/${TS_UTC}"

mkdir -p "${OUT}/logs" "${OUT}/fixtures" "${OUT}/snapshots"

echo "=============================================="
echo "PetCare PH61 CLOSURE PACK"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "=============================================="

need=(
  "FND/VERIFICATION_POLICY.json"
  "FND/VERIFICATION_POLICY.sha256"
  "FND/VERIFICATION_POLICY_CHANGELOG.md"
  "scripts/petcare_verification_policy_verify.py"
  "scripts/petcare_verification_policy_changelog_add.py"
  "scripts/petcare_verification_index_verify.py"
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
echo "=== STEP 2: DISCOVER REAL INDEX PATH (NO GUESSING) ==="
REAL_INDEX="$(python3 - <<'PY'
from pathlib import Path
base=Path("FND")
matches=sorted(p for p in base.rglob("*.json") if "VERIFICATION" in p.name.upper() and "INDEX" in p.name.upper())
if len(matches)!=1:
    raise SystemExit(f"FATAL: expected exactly 1 VERIFICATION*INDEX*.json under FND; found {len(matches)}: {matches}")
print(str(matches[0]))
PY
)"
echo "REAL_INDEX=${REAL_INDEX}" | tee "${OUT}/logs/index_discovery.log"

echo ""
echo "=== STEP 3: REAL INDEX VERIFY (WITH QUORUM ENFORCEMENT) ==="
set +e
python3 "${REPO_ROOT}/scripts/petcare_verification_index_verify.py" \
  --index "${REAL_INDEX}" \
  --print_index_digest \
  | tee "${OUT}/logs/index_verify_real.log"
rc=${PIPESTATUS[0]}
set -e
echo "REAL_INDEX_VERIFY_RC=${rc}" | tee -a "${OUT}/logs/index_verify_real.log"
# Do not force PASS here — repo may not yet produce 2 distinct meta verifiers in the real index.
# PH61 proof comes from fixtures below.
if [ "${rc}" -ne 0 ] && [ "${rc}" -ne 135 ]; then
  echo "FATAL: unexpected verifier rc=${rc} (expected 0 or 135)." | tee -a "${OUT}/logs/index_verify_real.log"
  exit 10
fi

echo ""
echo "=== STEP 4: FIXTURE NEGATIVE (EXPECT rc=135) ==="
cat > "${OUT}/fixtures/index_quorum_fail.json" <<'JSON'
[
  {"verifier_pack":"PETCARE-PH44B-CLOSURE"},
  {"verifier_pack":"PETCARE-PH44B-CLOSURE"}
]
JSON

set +e
python3 "${REPO_ROOT}/scripts/petcare_verification_index_verify.py" \
  --index "${OUT}/fixtures/index_quorum_fail.json" \
  --print_index_digest \
  | tee "${OUT}/logs/index_verify_fixture_fail.log"
rc_fail=${PIPESTATUS[0]}
set -e
echo "FIXTURE_FAIL_RC=${rc_fail}" | tee -a "${OUT}/logs/index_verify_fixture_fail.log"
if [ "${rc_fail}" -ne 135 ]; then
  echo "FATAL: fixture fail expected rc=135 but got rc=${rc_fail}" | tee -a "${OUT}/logs/index_verify_fixture_fail.log"
  exit 11
fi

echo ""
echo "=== STEP 5: FIXTURE POSITIVE (EXPECT rc=0) ==="
cat > "${OUT}/fixtures/index_quorum_pass.json" <<'JSON'
[
  {"verifier_pack":"PETCARE-PH44B-CLOSURE"},
  {"verifier_pack":"PETCARE-PH45B-CLOSURE"}
]
JSON

python3 "${REPO_ROOT}/scripts/petcare_verification_index_verify.py" \
  --index "${OUT}/fixtures/index_quorum_pass.json" \
  --print_index_digest \
  | tee "${OUT}/logs/index_verify_fixture_pass.log"

echo ""
echo "=== STEP 6: CHANGELOG APPEND (RECORD POLICY SHA) ==="
python3 "${REPO_ROOT}/scripts/petcare_verification_policy_changelog_add.py" \
  --pack "PH61-INDEX-QUORUM-ENFORCE(exit=135)" \
  --ts "${TS_UTC}" \
  | tee "${OUT}/logs/changelog_add.log"

echo ""
echo "=== STEP 7: CI GATES (REQUIRED) ==="
bash "${REPO_ROOT}/scripts/petcare_ci_gates.sh" \
  | tee "${OUT}/logs/ci_gates.log"

echo ""
echo "=== SNAPSHOT CONTROL FILES ==="
snap=(
  "FND/VERIFICATION_POLICY.json"
  "FND/VERIFICATION_POLICY.sha256"
  "FND/VERIFICATION_POLICY_CHANGELOG.md"
  "scripts/petcare_verification_index_verify.py"
  "scripts/petcare_ph61_closure_pack.sh"
)
for f in "${snap[@]}"; do
  mkdir -p "${OUT}/snapshots/$(dirname "${f}")"
  cp -p "${REPO_ROOT}/${f}" "${OUT}/snapshots/${f}"
done

echo ""
echo "=== MANIFEST (DETERMINISTIC ORDER) ==="
python3 - <<PY
import json
from pathlib import Path
out=Path("${OUT}")
files=[]
for p in sorted(out.rglob("*")):
    if p.is_file():
        files.append(str(p.relative_to(out)))
m={
  "phase":"${PHASE}",
  "timestamp_utc":"${TS_UTC}",
  "real_index_path":"${REAL_INDEX}",
  "files":files,
  "file_count":len(files),
}
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
