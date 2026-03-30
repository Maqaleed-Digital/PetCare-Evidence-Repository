#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACK="PETCARE-PH29B-CLOSURE"
TS_UTC="$(date -u +"%Y%m%dT%H%M%SZ")"
OUT_ROOT="${REPO}/evidence_output/${PACK}"
OUT_DIR="${OUT_ROOT}/${TS_UTC}"
PY="${REPO}/.venv/bin/python"

mkdir -p "${OUT_DIR}/snapshots"
mkdir -p "${OUT_DIR}/logs"

echo "=============================================="
echo "PetCare PH29B CLOSURE PACK"
echo "pack=${PACK}"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${REPO}"
echo "out=${OUT_DIR}"
echo "python_bin=${PY}"
echo "=============================================="

if [ ! -x "${PY}" ]; then
  echo "ERROR: venv python not found or not executable: ${PY}"
  exit 2
fi

echo ""
echo "=== PYTHON ==="
"${PY}" -V

echo ""
echo "=== TARGET FILES (SNAPSHOT) ==="
FILES=(
  "FND/CODE_SCAFFOLD/app.py"
  "FND/CODE_SCAFFOLD/api/routes_audit_verify.py"
  "scripts/petcare_ph29b_inject_audit_verify_routes.py"
  "TESTS/test_audit_verify_http_endpoint.py"
)

: > "${OUT_DIR}/closure_files.txt"
missing=0
for f in "${FILES[@]}"; do
  echo "${f}" >> "${OUT_DIR}/closure_files.txt"
  if [ -f "${REPO}/${f}" ]; then
    mkdir -p "${OUT_DIR}/snapshots/$(dirname "${f}")"
    cp -p "${REPO}/${f}" "${OUT_DIR}/snapshots/${f}"
    echo "SNAPSHOT_OK=${f}"
  else
    echo "SNAPSHOT_MISSING=${f}"
    echo "MISSING_FILE=${f}" >> "${OUT_DIR}/missing_files.txt"
    missing=1
  fi
done

if [ "${missing}" -ne 0 ]; then
  echo ""
  echo "ERROR: Missing required snapshot files. See:"
  echo "  ${OUT_DIR}/missing_files.txt"
  exit 3
fi

echo ""
echo "=== PYTEST (TARGETED) ==="
set +e
"${PY}" -m pytest -q "TESTS/test_audit_verify_http_endpoint.py" > "${OUT_DIR}/logs/pytest_targeted.log" 2>&1
rc1=$?
set -e
echo "PYTEST_TARGETED_RC=${rc1}"
tail -n 120 "${OUT_DIR}/logs/pytest_targeted.log" || true
if [ "${rc1}" -ne 0 ]; then
  echo "ERROR: Targeted pytest failed. Log:"
  echo "  ${OUT_DIR}/logs/pytest_targeted.log"
  exit 4
fi

echo ""
echo "=== PYTEST (FULL) ==="
set +e
"${PY}" -m pytest -q > "${OUT_DIR}/logs/pytest_full.log" 2>&1
rc2=$?
set -e
echo "PYTEST_FULL_RC=${rc2}"
tail -n 160 "${OUT_DIR}/logs/pytest_full.log" || true
if [ "${rc2}" -ne 0 ]; then
  echo "ERROR: Full pytest failed. Log:"
  echo "  ${OUT_DIR}/logs/pytest_full.log"
  exit 5
fi

echo ""
echo "=== ENV (pip freeze) ==="
"${PY}" -m pip freeze > "${OUT_DIR}/pip_freeze.txt" 2>&1 || true

echo ""
echo "=== SHA256 (DETERMINISTIC LIST) ==="
(
  cd "${OUT_DIR}" || exit 1
  find . -type f -print0 \
  | LC_ALL=C sort -z \
  | xargs -0 shasum -a 256
) > "${OUT_DIR}/closure_sha256.txt"

echo ""
echo "=== MANIFEST.json ==="
export OUT_DIR="${OUT_DIR}"
export REPO="${REPO}"
export PACK="${PACK}"
export TS_UTC="${TS_UTC}"
"${PY}" - <<'PY'
import json, os, platform, subprocess, sys, time
out_dir = os.environ.get("OUT_DIR")
repo = os.environ.get("REPO")
pack = os.environ.get("PACK")
ts = os.environ.get("TS_UTC")

def sh(cmd):
    try:
        return subprocess.check_output(cmd, cwd=repo, stderr=subprocess.STDOUT, text=True).strip()
    except Exception as e:
        return f"ERR:{type(e).__name__}"

manifest = {
    "pack": pack,
    "timestamp_utc": ts,
    "repo_root": repo,
    "python": sys.version.split()[0],
    "platform": platform.platform(),
    "git": {
        "head": sh(["git", "rev-parse", "HEAD"]),
        "status": sh(["git", "status", "-sb"]),
    },
    "artifacts": {
        "snapshots_dir": "snapshots",
        "pytest_targeted_log": "logs/pytest_targeted.log",
        "pytest_full_log": "logs/pytest_full.log",
        "pip_freeze": "pip_freeze.txt",
        "sha256": "closure_sha256.txt",
        "closure_files": "closure_files.txt",
    },
}
p = os.path.join(out_dir, "MANIFEST.json")
with open(p, "w", encoding="utf-8", newline="\n") as f:
    json.dump(manifest, f, indent=2, sort_keys=True)
print("WROTE", p)
PY

echo ""
echo "=== ZIP + ZIP.SHA256 ==="
cd "${OUT_ROOT}" || exit 1
BASE="$(basename "${OUT_DIR}")"
ZIP="${PACK}_${BASE}.zip"
rm -f "${ZIP}" "${ZIP}.sha256"
zip -r "${ZIP}" "${BASE}" >/dev/null
shasum -a 256 "${ZIP}" > "${ZIP}.sha256"

echo ""
echo "=== SUMMARY ==="
echo "OUT_DIR=${OUT_DIR}"
echo "ZIP=${OUT_ROOT}/${ZIP}"
echo "ZIP_SHA256=${OUT_ROOT}/${ZIP}.sha256"
echo "DONE"
