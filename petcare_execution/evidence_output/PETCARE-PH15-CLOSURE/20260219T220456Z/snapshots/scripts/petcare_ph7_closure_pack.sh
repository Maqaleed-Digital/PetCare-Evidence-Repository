#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

PY="${REPO_ROOT}/.venv/bin/python"
if [ ! -x "${PY}" ]; then
  echo "FAIL: missing venv python at ${PY}"
  exit 2
fi

if ! command -v zip >/dev/null 2>&1; then
  echo "FAIL: zip command not found"
  exit 3
fi

if command -v shasum >/dev/null 2>&1; then
  SHA_CMD="shasum -a 256"
elif command -v sha256sum >/dev/null 2>&1; then
  SHA_CMD="sha256sum"
else
  echo "FAIL: neither shasum nor sha256sum found"
  exit 4
fi

PACK="PETCARE-PH7-CLOSURE"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
BASE="${REPO_ROOT}/evidence_output/${PACK}"
OUT="${BASE}/${TS}"
ZIP_NAME="${PACK}_${TS}.zip"
ZIP_PATH="${BASE}/${ZIP_NAME}"

SMOKE_PORT="${SMOKE_PORT:-8004}"
HOST="${HOST:-127.0.0.1}"

mkdir -p "${OUT}"

CLOSURE_LOG="${OUT}/closure.log"
UNITTEST_LOG="${OUT}/unittest.log"
SMOKE_LOG="${OUT}/smoke.log"
LAND_LOG="${OUT}/land_pack.log"
SNAPSHOT_DIR="${OUT}/repo_snapshot"

exec > >(tee -a "${CLOSURE_LOG}") 2>&1

echo "=============================================="
echo "PetCare PH7 CLOSURE PACK"
echo "pack=${PACK}"
echo "timestamp_utc=${TS}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "zip=${ZIP_PATH}"
echo "smoke_host=${HOST}"
echo "smoke_port=${SMOKE_PORT}"
echo "store_backend=sqlite"
echo "python=$(${PY} --version 2>&1)"
echo "=============================================="
echo ""

echo "STEP 1: UNITTEST"
"${PY}" -m unittest discover -s "TESTS" -p "test_*.py" -v 2>&1 | tee "${UNITTEST_LOG}"
grep -qE "^Ran [0-9]+ tests?" "${UNITTEST_LOG}"
echo "UNITTEST: PASS"
echo ""

echo "STEP 2: START API SERVER (uvicorn) [sqlite backend]"
SERVER_LOG="${OUT}/uvicorn.log"
PID_FILE="${OUT}/uvicorn.pid"

set +e
PETCARE_STORE_BACKEND="sqlite" PORT="${SMOKE_PORT}" HOST="${HOST}" bash "scripts/run_api.sh" serve >"${SERVER_LOG}" 2>&1 &
UV_PID="$!"
set -e
echo "${UV_PID}" > "${PID_FILE}"

echo "uvicorn_pid=${UV_PID}"
echo "wait_for_health..."
OK=0
for i in 1 2 3 4 5 6 7 8 9 10; do
  r="$(curl -sS "http://${HOST}:${SMOKE_PORT}/health" 2>/dev/null || true)"
  echo "health_try_${i}=${r}" >> "${OUT}/health_poll.log"
  echo "${r}" | grep -q '"ok":true' && OK=1 && break
  sleep 0.4
done

if [ "${OK}" != "1" ]; then
  echo "FAIL: server health did not become ready"
  echo "uvicorn_log:"
  sed -n '1,220p' "${SERVER_LOG}" || true
  kill -9 "${UV_PID}" >/dev/null 2>&1 || true
  exit 10
fi

echo "SERVER: READY"
echo ""

echo "STEP 3: SMOKE [sqlite backend]"
PETCARE_STORE_BACKEND="sqlite" PORT="${SMOKE_PORT}" HOST="${HOST}" bash "scripts/run_api.sh" smoke 2>&1 | tee "${SMOKE_LOG}"
echo "SMOKE: PASS"
echo ""

echo "STEP 4: STOP API SERVER"
kill "${UV_PID}" >/dev/null 2>&1 || true
sleep 0.2
kill -9 "${UV_PID}" >/dev/null 2>&1 || true
echo "SERVER: STOPPED"
echo ""

echo "STEP 5: STORE LIFECYCLE OPS (isolated temp base_dir)"
OPS_DIR="${OUT}/ops"
mkdir -p "${OPS_DIR}"
OPS_JSON="${OPS_DIR}/ops_summary.json"

OPS_BASE="${OPS_DIR}/tenants"
TENANT="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
BACKUP="${OPS_DIR}/backup.sqlite"

"${PY}" - <<PY
import json
from pathlib import Path

from FND.CODE_SCAFFOLD.storage.sqlite_store import SqliteStore

ops_dir = Path("${OPS_DIR}").resolve()
base_dir = Path("${OPS_BASE}").resolve()
backup = Path("${BACKUP}").resolve()
tenant = "${TENANT}"

s = SqliteStore(base_dir=str(base_dir))

s.put(tenant_id=tenant, key="life:k1", value={"v": 1}, actor_id="ops")
integrity = s.integrity_check(tenant)

backup_path = s.backup_tenant_db(tenant_id=tenant, backup_path=str(backup))

s.put(tenant_id=tenant, key="life:k1", value={"v": 2}, actor_id="ops")
v2 = s.get(tenant_id=tenant, key="life:k1")

s.restore_tenant_db(tenant_id=tenant, backup_path=backup_path)
v_restored = s.get(tenant_id=tenant, key="life:k1")

meta_schema = s.get_meta(tenant_id=tenant, key="schema_version")

out = {
  "tenant": tenant,
  "base_dir": str(base_dir),
  "backup": str(backup),
  "integrity": integrity,
  "value_after_mutation": v2,
  "value_after_restore": v_restored,
  "meta_schema_version": meta_schema,
}

ops_dir.mkdir(parents=True, exist_ok=True)
(ops_dir / "ops_summary.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print("ops_summary_written", str((ops_dir / "ops_summary.json")))
PY

test -f "${OPS_JSON}"
echo "OPS_GOVERNANCE: PASS"
echo ""

echo "STEP 6: LAND PACK"
bash "scripts/petcare_land_pack.sh" 2>&1 | tee "${LAND_LOG}"
echo "LAND_PACK: PASS"
echo ""

echo "STEP 7: SNAPSHOT REPO"
mkdir -p "${SNAPSHOT_DIR}"
rsync -a \
  --exclude='.git' \
  --exclude='.venv' \
  --exclude='evidence_output' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.DS_Store' \
  "${REPO_ROOT}/" "${SNAPSHOT_DIR}/"

SNAP_COUNT="$(find "${SNAPSHOT_DIR}" -type f | wc -l | tr -d ' ')"
echo "snapshot_file_count=${SNAP_COUNT}"
echo ""

echo "STEP 8: GENERATE CLOSURE MANIFEST (for OUT dir)"
OUT_DIR="${OUT}" PACK_ID="${PACK}" TS_UTC="${TS}" "${PY}" - <<'PY'
import os, json, hashlib
from pathlib import Path

out = Path(os.environ["OUT_DIR"]).resolve()
pack = os.environ["PACK_ID"]
ts = os.environ["TS_UTC"]
manifest_path = out / "MANIFEST.json"

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

files = []
for p in sorted(out.rglob("*")):
    if p.is_dir():
        continue
    rel = p.relative_to(out).as_posix()
    if rel == "MANIFEST.json":
        continue
    st = p.stat()
    files.append({"path": rel, "bytes": int(st.st_size), "sha256": sha256_file(p)})

m = {
    "pack_id": pack,
    "timestamp_utc": ts,
    "out_dir": str(out),
    "file_count": len(files) + 1,
    "files": files,
}

manifest_path.write_text(json.dumps(m, indent=2, sort_keys=True) + "\n", encoding="utf-8")

m2 = json.loads(manifest_path.read_text(encoding="utf-8"))
st = manifest_path.stat()
m2["files"].append({"path": "MANIFEST.json", "bytes": int(st.st_size), "sha256": sha256_file(manifest_path)})
m2["files"].sort(key=lambda x: x["path"])
m2["file_count"] = len(m2["files"])
manifest_path.write_text(json.dumps(m2, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

echo "MANIFEST: PASS"
echo ""

echo "STEP 9: ZIP + SHA256"
mkdir -p "${BASE}"
cd "${BASE}" || exit 1
zip -r "${ZIP_NAME}" "${TS}" >/dev/null
${SHA_CMD} "${ZIP_NAME}" > "${ZIP_NAME}.sha256"

echo "ZIP=${ZIP_PATH}"
echo "SHA256=$(cut -d' ' -f1 "${ZIP_NAME}.sha256")"
echo ""
echo "CLOSURE PACK: PASS"
