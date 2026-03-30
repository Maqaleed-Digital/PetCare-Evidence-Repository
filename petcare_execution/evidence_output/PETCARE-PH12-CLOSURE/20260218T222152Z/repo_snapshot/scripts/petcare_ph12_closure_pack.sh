#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TS="$(python3 - <<'PY'
from datetime import datetime, timezone
print(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
PY
)"
PACK="PETCARE-PH12-CLOSURE"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PACK}"
OUT="${OUT_ROOT}/${TS}"
ZIP="${OUT_ROOT}/${PACK}_${TS}.zip"

echo "=============================================="
echo "PetCare PH12 CLOSURE PACK"
echo "pack=${PACK}"
echo "timestamp_utc=${TS}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "zip=${ZIP}"
echo "=============================================="

mkdir -p "${OUT}"

echo "=== REPO CONTEXT ===" | tee "${OUT}/00_context.txt"
cd "${REPO_ROOT}" || exit 1
pwd | tee -a "${OUT}/00_context.txt"
git status -sb | tee -a "${OUT}/00_context.txt" || true
git log -1 --oneline | tee -a "${OUT}/00_context.txt" || true

echo "=== GENERATE PH12 REGISTRY SHA256 (TAMPER-EVIDENT) ==="
python3 "scripts/petcare_ph12_registry_digest.py" | tee "${OUT}/01_registry_digest.txt"

echo "=== GENERATE PH12 POLICY DIGEST ARTIFACT ==="
python3 "scripts/petcare_ph12_policy_digest.py" | tee "${OUT}/02_policy_digest.txt"

echo "=== RUN UNITTEST ==="
python3 -m unittest -q 2>&1 | tee "${OUT}/03_unittest.txt"

echo "=== SNAPSHOT (PH12-RELEVANT FILES) ==="
SNAP="${OUT}/repo_snapshot"
mkdir -p "${SNAP}"
rsync -a \
  --exclude='.git' \
  --exclude='evidence_output' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  "${REPO_ROOT}/FND/security" "${SNAP}/FND/" >/dev/null 2>&1 || true
rsync -a \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  "${REPO_ROOT}/FND/CODE_SCAFFOLD/storage/export_bundle.py" "${SNAP}/FND/CODE_SCAFFOLD/storage/" >/dev/null 2>&1 || true
rsync -a \
  "${REPO_ROOT}/ops/ph12_gate_registry.json" "${SNAP}/ops/" >/dev/null 2>&1 || true
rsync -a \
  "${REPO_ROOT}/ops/ph12_gate_registry.sha256" "${SNAP}/ops/" >/dev/null 2>&1 || true
rsync -a \
  "${REPO_ROOT}/ops/ph12_policy_digest.json" "${SNAP}/ops/" >/dev/null 2>&1 || true
rsync -a \
  "${REPO_ROOT}/TESTS/test_ph12_"*".py" "${SNAP}/TESTS/" >/dev/null 2>&1 || true
rsync -a \
  "${REPO_ROOT}/scripts/petcare_ph12_"*".py" "${SNAP}/scripts/" >/dev/null 2>&1 || true
rsync -a \
  "${REPO_ROOT}/scripts/petcare_ph12_closure_pack.sh" "${SNAP}/scripts/" >/dev/null 2>&1 || true

echo "=== ENFORCE GATES ==="
python3 "scripts/petcare_ph12_enforce_gates.py" | tee "${OUT}/04_gate_enforce.json"

echo "=== CREATE MANIFEST.json (DETERMINISTIC) ==="
OUT="${OUT}" PACK="${PACK}" TS="${TS}" REPO_ROOT="${REPO_ROOT}" \
python3 - <<'PY'
import hashlib, json, os
out = os.environ["OUT"]
pack = os.environ["PACK"]
ts = os.environ["TS"]
repo_root = os.environ["REPO_ROOT"]

def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

records = []
for root, dirs, files in os.walk(out):
    dirs.sort()
    files.sort()
    for fn in files:
        p = os.path.join(root, fn)
        rel = os.path.relpath(p, out).replace("\\", "/")
        records.append({"path": rel, "sha256": sha256(p)})

manifest = {
    "manifest_version": "1.0",
    "pack": pack,
    "timestamp_utc": ts,
    "repo_root": repo_root,
    "file_count": len(records),
    "files": records
}

mp = os.path.join(out, "MANIFEST.json")
with open(mp, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False, sort_keys=True)
    f.write("\n")
print(mp)
PY

echo "=== ZIP + SHA256 ==="
mkdir -p "${OUT_ROOT}"
rm -f "${ZIP}" "${ZIP}.sha256"
(
  cd "${OUT_ROOT}" || exit 1
  zip -rq "${PACK}_${TS}.zip" "${TS}"
)
shasum -a 256 "${ZIP}" | tee "${ZIP}.sha256"

echo "=== STOP CONDITION CHECK ==="
python3 - <<'PY'
import json, os, sys
out_root = os.environ["OUT_ROOT"]
ts = os.environ["TS"]
pack = os.environ["PACK"]
out = os.path.join(out_root, ts)
manifest = os.path.join(out, "MANIFEST.json")
zip_path = os.path.join(out_root, f"{pack}_{ts}.zip")
sha_path = zip_path + ".sha256"
gate_json = os.path.join(out, "04_gate_enforce.json")

ok = True
if not os.path.exists(manifest): ok = False
if not os.path.exists(zip_path): ok = False
if not os.path.exists(sha_path): ok = False

gate_ok = False
if os.path.exists(gate_json):
    try:
        obj = json.load(open(gate_json, "r", encoding="utf-8"))
        gate_ok = bool(obj.get("ok") is True)
    except Exception:
        gate_ok = False
ok = ok and gate_ok

if ok:
    print(f"PASS: {pack} {ts}")
    sys.exit(0)
print(f"FAIL: {pack} {ts}")
sys.exit(2)
PY
