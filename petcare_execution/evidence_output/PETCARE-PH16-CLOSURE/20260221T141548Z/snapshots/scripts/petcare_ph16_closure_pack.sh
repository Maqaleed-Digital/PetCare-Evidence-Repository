#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

PACK_ID="PETCARE-PH16-CLOSURE"
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
echo "PetCare PH16 CLOSURE PACK"
echo "pack=${PACK_ID}"
echo "timestamp_utc=${ts}"
echo "repo_root=${REPO_ROOT}"
echo "out=${REPO_ROOT}/${OUT}"
echo "python_bin=${PY_BIN}"
echo "=============================================="

{
  echo "python_bin=${PY_BIN}"
  command -v "${PY_BIN}" || true
  "${PY_BIN}" -V || true
  "${PY_BIN}" -m pip -V || true
  echo "date_local=$(date)"
  echo "date_utc=$(date -u)"
} > "${OUT}/runtime.txt" 2>&1 || true

git rev-parse --show-toplevel > "${OUT}/git_toplevel.txt" 2>/dev/null || true
git status -sb > "${OUT}/git_status.txt" 2>/dev/null || true
git log -1 --oneline > "${OUT}/git_head.txt" 2>/dev/null || true

set +e
bash "scripts/petcare_ci_preflight.sh" > "${OUT}/ci_preflight.txt" 2>&1
PREFLIGHT_RC=$?
set -e
printf "ci_preflight_rc=%s\n" "${PREFLIGHT_RC}" > "${OUT}/ci_preflight_rc.txt"
if [ "${PREFLIGHT_RC}" -ne 0 ]; then
  record_fail "CI_PREFLIGHT_FAILED rc=${PREFLIGHT_RC}"
fi

set +e
bash "scripts/run_tests_deterministic.sh" > "${OUT}/pytest.txt" 2>&1
PYTEST_RC=$?
set -e
printf "pytest_rc=%s\n" "${PYTEST_RC}" > "${OUT}/pytest_rc.txt"
if [ "${PYTEST_RC}" -ne 0 ]; then
  record_fail "PYTEST_FAILED rc=${PYTEST_RC}"
fi

echo "=== POLICY DRIFT CHECK (LOGGED) ==="
set +e
bash "scripts/petcare_policy_drift_check.sh" > "${OUT}/policy_drift.txt" 2>&1
POLICY_RC=$?
set -e
printf "policy_drift_rc=%s\n" "${POLICY_RC}" > "${OUT}/policy_drift_rc.txt"
if [ "${POLICY_RC}" -ne 0 ]; then
  record_fail "POLICY_DRIFT_FAILED rc=${POLICY_RC}"
fi

echo "=== REGISTRY DRIFT CHECK (LOGGED) ==="
set +e
bash "scripts/petcare_registry_drift_check.sh" > "${OUT}/registry_drift.txt" 2>&1
REGISTRY_RC=$?
set -e
printf "registry_drift_rc=%s\n" "${REGISTRY_RC}" > "${OUT}/registry_drift_rc.txt"
if [ "${REGISTRY_RC}" -ne 0 ]; then
  record_fail "REGISTRY_DRIFT_FAILED rc=${REGISTRY_RC}"
fi

CLOSURE_LIST="${OUT}/closure_files.txt"
: > "${CLOSURE_LIST}"

add_file() { [ -f "$1" ] && echo "$1" >> "${CLOSURE_LIST}" || true; }
add_dir_files() { [ -d "$1" ] && find "$1" -type f -print | LC_ALL=C sort >> "${CLOSURE_LIST}" || true; }

add_file "pytest.ini"
add_file "requirements.txt"
add_file "app.py"
add_dir_files "FND"
add_dir_files "UI6"
add_dir_files "scripts"
add_dir_files "TESTS"
add_dir_files "tests"
add_dir_files "ops"

LC_ALL=C sort -u "${CLOSURE_LIST}" -o "${CLOSURE_LIST}"

SNAP="${OUT}/snapshots"
mkdir -p "${SNAP}"
: > "${OUT}/missing_files.txt"

while IFS= read -r f; do
  if [ -f "${f}" ]; then
    mkdir -p "${SNAP}/$(dirname "${f}")"
    cp -p "${f}" "${SNAP}/${f}"
  else
    echo "MISSING_FILE=${f}" >> "${OUT}/missing_files.txt"
  fi
done < "${CLOSURE_LIST}"

find "${OUT}" -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 > "${OUT}/closure_sha256_pre_manifest.txt"

export PETCARE_REPO_ROOT="${REPO_ROOT}"
export PETCARE_OUT_DIR="${OUT}"
export PETCARE_PACK_ID="${PACK_ID}"
export PETCARE_TS_UTC="${ts}"

"${PY_BIN}" - <<'PY' > "${OUT}/manifest_gen.txt" 2>&1
import json, os
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

def read_kv(p, key):
  t = read_text(p).strip()
  if not t.startswith(key + "="):
    return None
  try:
    return int(t.split("=", 1)[1].strip())
  except Exception:
    return None

pytest_rc = read_kv(os.path.join(out, "pytest_rc.txt"), "pytest_rc")
preflight_rc = read_kv(os.path.join(out, "ci_preflight_rc.txt"), "ci_preflight_rc")

policy_rc = read_kv(os.path.join(out, "policy_drift_rc.txt"), "policy_drift_rc")
registry_rc = read_kv(os.path.join(out, "registry_drift_rc.txt"), "registry_drift_rc")

status = "PASS" if (pytest_rc == 0 and preflight_rc == 0 and policy_rc == 0 and registry_rc == 0) else "FAIL"

manifest = {
  "pack_id": pack_id,
  "phase": "PH16",
  "name": "CI Required Checks + Drift Enforcement Closure Pack",
  "status": status,
  "timestamp_utc": ts,
  "repo_root": repo_root,
  "out_dir": out,
  "runtime": read_text(os.path.join(out, "runtime.txt")).strip(),
  "git": {
    "head": read_text(os.path.join(out, "git_head.txt")).strip(),
    "status": read_text(os.path.join(out, "git_status.txt")).strip()
  },
  "ci": {
    "preflight_rc": preflight_rc,
    "preflight_log_tail": "\n".join(read_text(os.path.join(out, "ci_preflight.txt")).splitlines()[-40:])
  },
  "tests": {
    "rc": pytest_rc,
    "raw_tail": "\n".join(read_text(os.path.join(out, "pytest.txt")).splitlines()[-40:])
  },
  "drift": {
    "policy_rc": policy_rc,
    "policy_tail": "\n".join(read_text(os.path.join(out, "policy_drift.txt")).splitlines()[-60:]),
    "registry_rc": registry_rc,
    "registry_tail": "\n".join(read_text(os.path.join(out, "registry_drift.txt")).splitlines()[-60:])
  },
  "artifacts": {
    "runtime": "runtime.txt",
    "ci_preflight": "ci_preflight.txt",
    "ci_preflight_rc": "ci_preflight_rc.txt",
    "pytest_log": "pytest.txt",
    "pytest_rc": "pytest_rc.txt",
    "policy_drift": "policy_drift.txt",
    "policy_drift_rc": "policy_drift_rc.txt",
    "registry_drift": "registry_drift.txt",
    "registry_drift_rc": "registry_drift_rc.txt",
    "closure_sha256_pre_manifest": "closure_sha256_pre_manifest.txt",
    "fail_marker": "FAIL_MARKER.txt",
    "manifest_gen_log": "manifest_gen.txt"
  },
  "zip": {"path": None, "sha256": None}
}

p = os.path.join(out, "MANIFEST.json")
with open(p, "w", encoding="utf-8") as f:
  json.dump(manifest, f, indent=2, sort_keys=True)
  f.write("\n")
print("MANIFEST_WRITTEN", p)
PY

test -f "${OUT}/MANIFEST.json"

mkdir -p "${OUT_ROOT}"
cd "${OUT_ROOT}" || exit 1
BASE="$(basename "${OUT}")"
ZIP="${PACK_ID}_${BASE}.zip"
rm -f "${ZIP}" "${ZIP}.sha256"
zip -r "${ZIP}" "${BASE}" >/dev/null
shasum -a 256 "${ZIP}" > "${ZIP}.sha256"
ZIP_SHA="$(cut -d' ' -f1 < "${ZIP}.sha256")"
cd "${REPO_ROOT}" || exit 1

export PETCARE_ZIP_SHA256="${ZIP_SHA}"
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

find "${OUT}" -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 > "${OUT}/closure_sha256_final.txt"

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
print("CI=", m.get("ci"))
print("TESTS=", m.get("tests"))
print("ZIP=", m.get("zip"))
PY

"${PY_BIN}" - <<'PY' "${OUT}/MANIFEST.json"
import json, sys
m=json.load(open(sys.argv[1],"r",encoding="utf-8"))
sys.exit(0 if m.get("status")=="PASS" else 1)
PY
