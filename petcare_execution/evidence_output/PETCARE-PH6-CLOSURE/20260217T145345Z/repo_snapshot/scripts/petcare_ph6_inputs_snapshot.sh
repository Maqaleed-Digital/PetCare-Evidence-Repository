#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

TS="$(date -u +%Y%m%dT%H%M%SZ)"
PACK="PETCARE-PH6-INPUT-SNAPSHOT"
OUT="evidence_output/${PACK}/${TS}"
mkdir -p "${OUT}"

echo "=============================================="
echo "PetCare PH6 INPUT SNAPSHOT"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "timestamp_utc=${TS}"
echo "=============================================="

save () {
  local p="$1"
  local name
  name="$(echo "$p" | sed 's|/|__|g')"
  if [ -f "${REPO_ROOT}/${p}" ]; then
    cp -f "${REPO_ROOT}/${p}" "${OUT}/${name}"
    echo "CAPTURED ${p}"
  else
    echo "MISSING  ${p}"
  fi
}

echo ""
echo "STEP 1: CAPTURE KEY FILES"
save "FND/CODE_SCAFFOLD/storage/sqlite_store.py"
save "FND/CODE_SCAFFOLD/storage/memory_store.py"
save "FND/CODE_SCAFFOLD/storage/export_bundle.py"
save "FND/CODE_SCAFFOLD/storage/__init__.py"
save "FND/CODE_SCAFFOLD/interfaces/storage_interface.py"
save "FND/CODE_SCAFFOLD/tenant_isolation_guard.py"
save "FND/CODE_SCAFFOLD/app.py"
save "scripts/run_api.sh"
save "scripts/petcare_land_pack.sh"
save "scripts/_manifest_gen.py"
save "scripts/petcare_ph5_closure_pack.sh"

echo ""
echo "STEP 2: RECORD TEST LIST"
if [ -d "TESTS" ]; then
  find "TESTS" -type f -name "test_*.py" | LC_ALL=C sort > "${OUT}/TESTS_list.txt"
  echo "WROTE ${OUT}/TESTS_list.txt"
else
  echo "NO TESTS DIR"
fi

echo ""
echo "STEP 3: RECORD TREE (SHALLOW)"
find . -maxdepth 4 -type f \
  -not -path "./.git/*" \
  -not -path "./.venv/*" \
  -not -path "./__pycache__/*" \
  -not -path "./evidence_output/*" \
  | LC_ALL=C sort | sed -n '1,260p' > "${OUT}/tree_maxdepth4.txt"
echo "WROTE ${OUT}/tree_maxdepth4.txt"

echo ""
echo "STEP 4: ZIP + SHA256"
ZIP="evidence_output/${PACK}/${PACK}_${TS}.zip"
rm -f "${ZIP}" "${ZIP}.sha256" || true
( cd "evidence_output/${PACK}" && zip -r "${PACK}_${TS}.zip" "${TS}" >/dev/null )

if command -v shasum >/dev/null 2>&1; then
  shasum -a 256 "${ZIP}" | awk '{print $1}' > "${ZIP}.sha256"
elif command -v sha256sum >/dev/null 2>&1; then
  sha256sum "${ZIP}" | awk '{print $1}' > "${ZIP}.sha256"
else
  echo "FAIL: neither shasum nor sha256sum found"
  exit 2
fi

echo "ZIP=${ZIP}"
echo "SHA256=$(cat "${ZIP}.sha256")"
echo ""
echo "DONE"
echo "RUN_DIR=${OUT}"
