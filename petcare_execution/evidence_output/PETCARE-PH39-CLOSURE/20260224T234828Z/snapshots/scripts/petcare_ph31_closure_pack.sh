#!/usr/bin/env bash
set -euo pipefail

# ==============================================
# PetCare PH31 CLOSURE PACK
# Domain: CI Gate Enforcement (Production-Ready)
# Artifacts: snapshots + logs + MANIFEST.json + zip + sha256 + in-script sha verify
# ==============================================

# ----------------------------
# Repo root resolution
# ----------------------------
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO}"

PACK="PETCARE-PH31-CLOSURE"
TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_ROOT="${REPO}/evidence_output/${PACK}"
OUT_DIR="${OUT_ROOT}/${TS_UTC}"
PY="${REPO}/.venv/bin/python"

mkdir -p "${OUT_DIR}/snapshots" "${OUT_DIR}/logs"

echo "=============================================="
echo "PetCare PH31 CLOSURE PACK"
echo "pack=${PACK}"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${REPO}"
echo "out=${OUT_DIR}"
echo "python_bin=${PY}"
echo "cwd=$(pwd)"
echo "=============================================="

echo ""
echo "=== PYTHON ==="
if [ ! -x "${PY}" ]; then
  echo "FAIL: venv python missing: ${PY}"
  exit 2
fi
"${PY}" -V

# ----------------------------
# WORKFLOW ENFORCEMENT GATE
# ----------------------------
echo ""
echo "=== WORKFLOW ENFORCEMENT GATE ==="
WF_DIR="${REPO}/.github/workflows"
if [ ! -d "${WF_DIR}" ]; then
  echo "FAIL: .github/workflows directory missing"
  exit 10
fi

WF_COUNT="$(find "${WF_DIR}" -type f \( -name "*.yml" -o -name "*.yaml" \) | wc -l | tr -d ' ')"
if [ "${WF_COUNT}" -eq 0 ]; then
  echo "FAIL: No workflow files found"
  exit 11
fi
echo "WORKFLOWS_FOUND=${WF_COUNT}"

# ----------------------------
# REQUIRED FILES POLICY GATE
# ----------------------------
# Policy: REQUIRED must exist or hard fail.
# Optional: snapshot if present (do not fail).
# ----------------------------
echo ""
echo "=== REQUIRED FILES POLICY GATE ==="

snapshot_file () {
  local rel="$1"
  local abs="${REPO}/${rel}"
  echo "${rel}"
  if [ ! -f "${abs}" ]; then
    echo "FAIL: missing required file: ${rel}"
    exit 12
  fi
  mkdir -p "${OUT_DIR}/snapshots/$(dirname "${rel}")"
  cp -p "${abs}" "${OUT_DIR}/snapshots/${rel}"
  echo "SNAPSHOT_OK=${rel}"
}

snapshot_optional_file () {
  local rel="$1"
  local abs="${REPO}/${rel}"
  echo "${rel}"
  if [ -f "${abs}" ]; then
    mkdir -p "${OUT_DIR}/snapshots/$(dirname "${rel}")"
    cp -p "${abs}" "${OUT_DIR}/snapshots/${rel}"
    echo "SNAPSHOT_OK=${rel}"
  else
    echo "OPTIONAL_MISSING=${rel}"
  fi
}

snapshot_dir () {
  local rel="$1"
  local abs="${REPO}/${rel}"
  echo "${rel}/"
  if [ ! -d "${abs}" ]; then
    echo "FAIL: missing required dir: ${rel}"
    exit 13
  fi
  mkdir -p "${OUT_DIR}/snapshots/$(dirname "${rel}")"
  rm -rf "${OUT_DIR}/snapshots/${rel}"
  cp -R "${abs}" "${OUT_DIR}/snapshots/${rel}"
  echo "SNAPSHOT_OK_DIR=${rel}"
}

# Required runtime/project files (production-ready surface)
snapshot_file "pytest.ini"
snapshot_file "requirements.txt"
snapshot_file "requirements-dev.txt"
snapshot_file "Makefile"
snapshot_file "scripts/petcare_land_pack.sh"
snapshot_file "scripts/petcare_increment_close.sh"
snapshot_file "scripts/petcare_audit_verify.py"
snapshot_dir  ".github"
snapshot_file "pyproject.toml"

# Lockfile: REQUIRED by policy (must have one)
# Acceptable lockfiles list
LOCK_CANDIDATES=("requirements.lock" "poetry.lock" "uv.lock" "pdm.lock" "Pipfile.lock")
LOCK_FOUND=""
for lf in "${LOCK_CANDIDATES[@]}"; do
  if [ -f "${REPO}/${lf}" ]; then
    LOCK_FOUND="${lf}"
    break
  fi
done

if [ -z "${LOCK_FOUND}" ]; then
  echo "FAIL: lockfile required by policy but none found (${LOCK_CANDIDATES[*]})"
  exit 14
fi

snapshot_file "${LOCK_FOUND}"
echo "LOCKFILE=${LOCK_FOUND}"

# Optional extras (do not fail)
snapshot_optional_file "requirements-dev.lock"
snapshot_optional_file "README.md"

# ----------------------------
# CI DRY-RUN GATE (LOCAL)
# ----------------------------
echo ""
echo "=== CI DRY-RUN GATE ==="

set +e
"${PY}" -m pytest --version | tee "${OUT_DIR}/logs/pytest_version.txt"
RC_VER=${PIPESTATUS[0]}
set -e
if [ "${RC_VER}" -ne 0 ]; then
  echo "FAIL: pytest --version failed rc=${RC_VER}"
  exit 15
fi

# Run unit tests (safe local simulation)
echo ""
echo "RUN=pytest -q"
set +e
"${PY}" -m pytest -q | tee "${OUT_DIR}/logs/pytest_run.log"
RC_TEST=${PIPESTATUS[0]}
set -e
if [ "${RC_TEST}" -ne 0 ]; then
  echo "FAIL: pytest run failed rc=${RC_TEST}"
  exit 16
fi

# ----------------------------
# Inventory workflows list
# ----------------------------
echo ""
echo "=== INVENTORY: WORKFLOWS ==="
set +e
find "${WF_DIR}" -type f \( -name "*.yml" -o -name "*.yaml" \) -print0 \
| LC_ALL=C sort -z \
| xargs -0 -I{} echo "{}" \
| sed "s#^${REPO}/##" \
| tee "${OUT_DIR}/logs/workflows_list.txt"
set -e
echo "WROTE=${OUT_DIR}/logs/workflows_list.txt"

# ----------------------------
# GIT CONTEXT (NON-FATAL)
# ----------------------------
echo ""
echo "=== GIT CONTEXT (NON-FATAL) ==="
set +e
(
  echo "TS_UTC=${TS_UTC}"
  echo "REPO=${REPO}"
  git rev-parse --is-inside-work-tree 2>/dev/null && git status --porcelain=v1 2>/dev/null
  echo "---"
  git rev-parse HEAD 2>/dev/null
  git rev-parse --abbrev-ref HEAD 2>/dev/null
) > "${OUT_DIR}/logs/git_context.txt"
set -e
echo "WROTE=${OUT_DIR}/logs/git_context.txt"

# ----------------------------
# MANIFEST (deterministic)
# ----------------------------
echo ""
echo "=== MANIFEST ==="
export OUT_DIR PACK TS_UTC
"${PY}" - <<'PY'
import hashlib, json, os, sys

out_dir = os.environ.get("OUT_DIR")
pack = os.environ.get("PACK")
ts_utc = os.environ.get("TS_UTC")

if not out_dir or not pack or not ts_utc:
    print("ERROR: OUT_DIR/PACK/TS_UTC not set")
    sys.exit(2)

repo = os.path.abspath(os.getcwd())

def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

files = []
for root, _, filenames in os.walk(out_dir):
    for fn in filenames:
        ap = os.path.join(root, fn)
        rp = os.path.relpath(ap, out_dir).replace("\\", "/")
        files.append((rp, ap))

files.sort(key=lambda x: x[0])

manifest = {
    "pack": pack,
    "timestamp_utc": ts_utc,
    "repo_root": repo,
    "out_dir": os.path.abspath(out_dir),
    "files": [{"path": rp, "sha256": sha256_file(ap)} for rp, ap in files],
}

p = os.path.join(out_dir, "MANIFEST.json")
with open(p, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, sort_keys=True)

print(f"WROTE={p}")
print(f"FILE_COUNT={len(files)}")
PY

# ----------------------------
# ZIP & SHA
# ----------------------------
echo ""
echo "=== ZIP ==="
cd "${OUT_ROOT}" || exit 1
BASE="$(basename "${OUT_DIR}")"
ZIP="${PACK}_${BASE}.zip"
rm -f "${ZIP}" "${ZIP}.sha256"
zip -r "${ZIP}" "${BASE}" >/dev/null
shasum -a 256 "${ZIP}" > "${ZIP}.sha256"
echo "zip=${OUT_ROOT}/${ZIP}"
echo "sha=${OUT_ROOT}/${ZIP}.sha256"

# ----------------------------
# ZIP SHA VERIFY (IN-SCRIPT)
# ----------------------------
echo ""
echo "=== ZIP SHA VERIFY (IN-SCRIPT) ==="
cd "${OUT_ROOT}" || exit 1
if shasum -a 256 -c "${ZIP}.sha256" >/dev/null 2>&1; then
  echo "ZIP_SHA_VERIFY=PASS"
else
  echo "ZIP_SHA_VERIFY=FAIL"
  exit 17
fi

echo ""
echo "=== SUMMARY ==="
echo "OUT=${OUT_DIR}"
echo "ZIP=${OUT_ROOT}/${ZIP}"
echo "DONE"
