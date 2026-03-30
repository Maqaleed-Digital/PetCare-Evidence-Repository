#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

PACK_ID="PETCARE-PH13-CLOSURE"
ts="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_ROOT="evidence_output/${PACK_ID}"
OUT="${OUT_ROOT}/${ts}"
mkdir -p "${OUT}"

PY_BIN="python3"
if [ -x ".venv/bin/python" ]; then
  PY_BIN=".venv/bin/python"
fi

FAIL_MARKER="${OUT}/FAIL_MARKER.txt"
: > "${FAIL_MARKER}"

record_fail() {
  local msg="$1"
  echo "${msg}" >> "${FAIL_MARKER}"
}

echo "=============================================="
echo "PetCare PH13 CLOSURE PACK"
echo "pack=${PACK_ID}"
echo "timestamp_utc=${ts}"
echo "repo_root=${REPO_ROOT}"
echo "out=${REPO_ROOT}/${OUT}"
echo "python_bin=${PY_BIN}"
echo "=============================================="

echo "=== CAPTURE RUNTIME CONTEXT ==="
{
  echo "python_bin=${PY_BIN}"
  command -v "${PY_BIN}" || true
  "${PY_BIN}" -V || true
  "${PY_BIN}" -m pip -V || true
  echo "date_local=$(date)"
  echo "date_utc=$(date -u)"
} > "${OUT}/runtime.txt" 2>&1 || true

echo "=== CAPTURE GIT CONTEXT ==="
git rev-parse --show-toplevel > "${OUT}/git_toplevel.txt" 2>/dev/null || true
git status -sb > "${OUT}/git_status.txt" 2>/dev/null || true
git log -1 --oneline > "${OUT}/git_head.txt" 2>/dev/null || true

echo "=== RUN TESTS (DETERMINISTIC LOG) ==="
TEST_LOG="${OUT}/pytest.txt"
PYTEST_RC=127

set +e
"${PY_BIN}" -c "import pytest; print('pytest_version=', pytest.__version__)" > "${OUT}/pytest_version.txt" 2>&1
HAVE_PYTEST=$?
if [ "${HAVE_PYTEST}" -eq 0 ]; then
  "${PY_BIN}" -m pytest -q > "${TEST_LOG}" 2>&1
  PYTEST_RC=$?
else
  echo "PYTEST_MISSING" > "${TEST_LOG}"
  cat "${OUT}/pytest_version.txt" >> "${TEST_LOG}" 2>/dev/null || true
  PYTEST_RC=127
fi
set -e

printf "pytest_rc=%s\n" "${PYTEST_RC}" > "${OUT}/pytest_rc.txt"

if [ "${PYTEST_RC}" -ne 0 ]; then
  if [ "${PYTEST_RC}" -eq 127 ]; then
    record_fail "PYTEST_MISSING rc=127 (bootstrap: python3 -m venv .venv && .venv/bin/python -m pip install pytest)"
  else
    record_fail "PYTEST_FAILED rc=${PYTEST_RC}"
  fi
fi

echo "=== BUILD CLOSURE FILE LIST ==="
CLOSURE_LIST="${OUT}/closure_files.txt"
: > "${CLOSURE_LIST}"

add_file() {
  local f="$1"
  if [ -f "${f}" ]; then
    echo "${f}" >> "${CLOSURE_LIST}"
  fi
}

add_dir_files() {
  local d="$1"
  if [ -d "${d}" ]; then
    find "${d}" -type f -print | LC_ALL=C sort >> "${CLOSURE_LIST}"
  fi
}

add_file "README.md"
add_file "app.py"
add_dir_files "FND"
add_dir_files "UI6"
add_dir_files "docs"
add_dir_files "scripts"
add_dir_files "tests"
add_file ".venv/pyvenv.cfg"

LC_ALL=C sort -u "${CLOSURE_LIST}" -o "${CLOSURE_LIST}"

echo "=== SNAPSHOT FILES (COPY) ==="
SNAP="${OUT}/snapshots"
mkdir -p "${SNAP}"

MISSING_TXT="${OUT}/missing_files.txt"
: > "${MISSING_TXT}"

while IFS= read -r f; do
  if [ -f "${f}" ]; then
    mkdir -p "${SNAP}/$(dirname "${f}")"
    cp -p "${f}" "${SNAP}/${f}"
  else
    echo "MISSING_FILE=${f}" >> "${MISSING_TXT}"
  fi
done < "${CLOSURE_LIST}"

echo "=== HASH PACK TREE (PRE-MANIFEST) ==="
find "${OUT}" -type f -print0 \
| LC_ALL=C sort -z \
| xargs -0 shasum -a 256 \
> "${OUT}/closure_sha256_pre_manifest.txt"

echo "=== GENERATE MANIFEST.json (PRE-ZIP) ==="
export PETCARE_REPO_ROOT="${REPO_ROOT}"
export PETCARE_OUT_DIR="${OUT}"
export PETCARE_PACK_ID="${PACK_ID}"
export PETCARE_TS_UTC="${ts}"

set +e
"${PY_BIN}" - <<'PY' > "${OUT}/manifest_gen.txt" 2>&1
import json, os, re

repo_root = os.environ["PETCARE_REPO_ROOT"]
out_rel = os.environ["PETCARE_OUT_DIR"]
pack_id = os.environ["PETCARE_PACK_ID"]
ts = os.environ["PETCARE_TS_UTC"]

out = os.path.join(repo_root, out_rel)

def read_text(p):
  try:
    with open(p, "r", encoding="utf-8", errors="replace") as f:
      return f.read()
  except FileNotFoundError:
    return ""

pytest_txt = read_text(os.path.join(out, "pytest.txt"))
pytest_rc_txt = read_text(os.path.join(out, "pytest_rc.txt")).strip()

passed = None
m = re.search(r"^(\d+) passed", pytest_txt, flags=re.M)
if m:
  passed = int(m.group(1))

rc = None
if "pytest_rc=" in pytest_rc_txt:
  try:
    rc = int(pytest_rc_txt.split("=", 1)[1].strip())
  except Exception:
    rc = None

status = "PASS" if rc == 0 else "FAIL"

manifest = {
  "pack_id": pack_id,
  "phase": "PH13",
  "name": "Operational Governance Hardening Closure Pack",
  "status": status,
  "timestamp_utc": ts,
  "repo_root": repo_root,
  "out_dir": out,
  "runtime": read_text(os.path.join(out, "runtime.txt")).strip(),
  "git": {
    "head": read_text(os.path.join(out, "git_head.txt")).strip(),
    "status": read_text(os.path.join(out, "git_status.txt")).strip()
  },
  "tests": {
    "rc": rc,
    "passed": passed,
    "raw_tail": "\n".join(pytest_txt.strip().splitlines()[-40:]) if pytest_txt.strip() else ""
  },
  "artifacts": {
    "runtime": "runtime.txt",
    "pytest_log": "pytest.txt",
    "pytest_rc": "pytest_rc.txt",
    "closure_sha256_pre_manifest": "closure_sha256_pre_manifest.txt",
    "fail_marker": "FAIL_MARKER.txt",
    "manifest_gen_log": "manifest_gen.txt"
  },
  "zip": {
    "path": None,
    "sha256": None
  }
}

p = os.path.join(out, "MANIFEST.json")
with open(p, "w", encoding="utf-8") as f:
  json.dump(manifest, f, indent=2, sort_keys=True)
  f.write("\n")
print("MANIFEST_WRITTEN", p)
PY
MANIFEST_RC=$?
set -e

if [ "${MANIFEST_RC}" -ne 0 ] || [ ! -f "${OUT}/MANIFEST.json" ]; then
  record_fail "MANIFEST_GEN_FAILED rc=${MANIFEST_RC}"
  echo "ERROR: manifest generation failed. See ${OUT}/manifest_gen.txt"
  exit 1
fi

echo "=== BUILD ZIP + ZIP.SHA256 ==="
mkdir -p "${OUT_ROOT}"
cd "${OUT_ROOT}" || exit 1
BASE="$(basename "${OUT}")"
ZIP="${PACK_ID}_${BASE}.zip"
rm -f "${ZIP}" "${ZIP}.sha256"
zip -r "${ZIP}" "${BASE}" >/dev/null
shasum -a 256 "${ZIP}" > "${ZIP}.sha256"
ZIP_SHA="$(cut -d' ' -f1 < "${ZIP}.sha256")"
cd "${REPO_ROOT}" || exit 1

echo "=== PATCH MANIFEST.json WITH ZIP INFO ==="
export PETCARE_ZIP_SHA256="${ZIP_SHA}"
set +e
"${PY_BIN}" - <<'PY' >> "${OUT}/manifest_gen.txt" 2>&1
import json, os
repo_root = os.environ["PETCARE_REPO_ROOT"]
out_rel = os.environ["PETCARE_OUT_DIR"]
pack_id = os.environ["PETCARE_PACK_ID"]
zip_sha = os.environ["PETCARE_ZIP_SHA256"]

out = os.path.join(repo_root, out_rel)
p = os.path.join(out, "MANIFEST.json")
m = json.load(open(p, "r", encoding="utf-8"))
zip_rel = os.path.join("..", f"{pack_id}_{os.path.basename(out)}.zip")
m["zip"]["path"] = zip_rel
m["zip"]["sha256"] = zip_sha
with open(p, "w", encoding="utf-8") as f:
  json.dump(m, f, indent=2, sort_keys=True)
  f.write("\n")
print("MANIFEST_PATCHED_ZIP", zip_rel, zip_sha)
PY
PATCH_RC=$?
set -e

if [ "${PATCH_RC}" -ne 0 ]; then
  record_fail "MANIFEST_PATCH_FAILED rc=${PATCH_RC}"
  echo "ERROR: manifest patch failed. See ${OUT}/manifest_gen.txt"
  exit 1
fi

echo "=== HASH PACK TREE (FINAL) ==="
find "${OUT}" -type f -print0 \
| LC_ALL=C sort -z \
| xargs -0 shasum -a 256 \
> "${OUT}/closure_sha256_final.txt"

echo "=== SUMMARY ==="
echo "OUT=${OUT}"
echo "MANIFEST=${OUT}/MANIFEST.json"
echo "ZIP=${OUT_ROOT}/${PACK_ID}_${ts}.zip"
echo "ZIP_SHA256=${OUT_ROOT}/${PACK_ID}_${ts}.zip.sha256"
"${PY_BIN}" - <<PY
import json
p="${OUT}/MANIFEST.json"
m=json.load(open(p,"r",encoding="utf-8"))
print("STATUS=", m.get("status"))
print("TESTS=", m.get("tests"))
print("ZIP=", m.get("zip"))
PY

if "${PY_BIN}" - <<'PY' "${OUT}/MANIFEST.json"
import json, sys
m=json.load(open(sys.argv[1],"r",encoding="utf-8"))
sys.exit(0 if m.get("status")=="PASS" else 1)
PY
then
  exit 0
else
  echo "PH13 completed with FAIL status (deterministic evidence produced)."
  exit 1
fi
