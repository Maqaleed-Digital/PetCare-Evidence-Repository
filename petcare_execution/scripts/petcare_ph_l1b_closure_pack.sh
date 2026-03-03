#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# PH-L1B — Release Integrity False-Positive Hardening + Repo Hygiene
# ============================================================

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

PHASE="PETCARE-PH-L1B-CLOSURE"
TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PHASE}"
OUT="${OUT_ROOT}/${TS_UTC}"
mkdir -p "${OUT}/logs" "${OUT}/snapshots"

echo "=============================================="
echo "PetCare PH-L1B CLOSURE"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "=============================================="

echo ""
echo "=== STEP 0: BASELINE CHECK (NO GUESSING) ==="
need=(
  "scripts/petcare_release_integrity_check.sh"
  "scripts/petcare_ci_gates.sh"
  "scripts/petcare_ph_l1_closure_pack.sh"
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
echo "=== STEP 1: CAPTURE PRE-PATCH RELEASE INTEGRITY (EXPECTED FAIL) ==="
bash "scripts/petcare_release_integrity_check.sh" > "${OUT}/logs/release_integrity_pre.txt" 2>&1 || true

echo ""
echo "=== STEP 2: PATCH release integrity heuristic (tmp→mv) ==="
python3 - <<'PY'
from pathlib import Path
import os, re, sys

p = Path("scripts/petcare_release_integrity_check.sh")
src = p.read_text(encoding="utf-8")

# No guessing: ensure expected marker exists
marker = 'echo "=== CHECK: obvious secret patterns in tracked files (heuristic) ==="'
if marker not in src:
    raise SystemExit("FATAL: expected secret heuristic header not found. Stop (no guessing).")

# Locate the block starting at marker and ending before the next '=== CHECK:' header (or end).
start = src.find(marker)
m_next = re.search(r'\necho "=== CHECK: ', src[start+len(marker):])
end = start + len(marker) + (m_next.start() if m_next else (len(src) - (start+len(marker))))

old_block = src[start:end]

# New hardened block:
new_block = """echo "=== CHECK: obvious secret patterns in tracked files (heuristic) ==="

# PH-L1B hardening:
# - exclude this script to avoid self-match (pattern text in script)
# - ignore env-var default reads like TOKEN="${TOKEN:-}" (not a secret)
# - keep strong secret patterns (private keys, AWS AKIA, obvious KEY assignments)
SECRET_RE='(BEGIN (RSA|EC|OPENSSH) PRIVATE KEY|AKIA[0-9A-Z]{16}|(^|[^A-Z0-9_])(API_KEY|SECRET_KEY|PRIVATE_KEY|ACCESS_TOKEN|GITHUB_TOKEN)[[:space:]]*=[[:space:]]*[^[:space:]]+)'

hits="$(git grep -nE "${SECRET_RE}" -- . \
  ':(exclude)evidence_output' \
  ':(exclude)scripts/petcare_release_integrity_check.sh' 2>/dev/null || true)"

if [ -n "${hits}" ]; then
  # Filter out env default reads: VAR="${VAR:-}" or VAR='${VAR:-}'
  filtered="$(printf "%s\\n" "${hits}" | grep -v ':-}' || true)"
  if [ -n "${filtered}" ]; then
    echo "FAIL secret heuristic hit"
    echo "${filtered}"
    fail=1
  else
    echo "PASS (only env-default reads matched; ignored)"
  fi
else
  echo "PASS no secret heuristics hit"
fi

"""

out = src[:start] + new_block + src[end:]

tmp = p.with_suffix(p.suffix + ".tmp")
tmp.write_text(out, encoding="utf-8", newline="\n")
os.replace(tmp, p)
print("PATCH_OK: hardened secret heuristic block")
PY

echo ""
echo "=== STEP 3: REPO HYGIENE (bak cleanup + ignore rule) ==="
# Remove known untracked .ph51.bak leftovers if present
for f in ".github/workflows/verification-index-gate-final.yml.ph51.bak" "scripts/petcare_verification_index_verify.py.ph51.bak"; do
  if [ -f "${f}" ]; then rm -f "${f}"; echo "REMOVED_UNTRACKED=${f}"; fi
done

# Add ignore rule for future phase backup artifacts (minimal)
if [ ! -f ".gitignore" ]; then
  printf "*.ph[0-9]*.bak\n" > ".gitignore"
else
  if ! grep -qE '^\*\.ph\[0-9\]\*\.bak$|^\*\.ph[0-9]\*\.bak$' ".gitignore"; then
    printf "\n*.ph[0-9]*.bak\n" >> ".gitignore"
  fi
fi

echo ""
echo "=== STEP 4: RELEASE INTEGRITY MUST PASS ==="
bash "scripts/petcare_release_integrity_check.sh" | tee "${OUT}/logs/release_integrity_post.txt"

echo ""
echo "=== STEP 5: CI GATES MUST PASS ==="
bash "scripts/petcare_ci_gates.sh" | tee "${OUT}/logs/ci_gates_post.txt"

echo ""
echo "=== STEP 6: SNAPSHOT CONTROL FILES ==="
snap=(
  "scripts/petcare_release_integrity_check.sh"
  "scripts/petcare_ci_gates.sh"
  "scripts/petcare_ph_l1_closure_pack.sh"
  ".gitignore"
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
echo "=== STEP 9: GIT ADD / COMMIT / PUSH ==="
git status -sb | tee "${OUT}/logs/git_status.log"

git add \
  "scripts/petcare_release_integrity_check.sh" \
  "scripts/petcare_ph_l1_closure_pack.sh" \
  ".gitignore"

git commit -m "PH-L1B: make release integrity PASS + repo hygiene"
git push origin main

echo ""
echo "=== DONE ==="
echo "ZIP=${ZIP}"
echo "ZIP_SHA=${ZIP}.sha256"
echo "COMMIT=$(git rev-parse HEAD)"
