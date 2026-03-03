#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# PH-L7 — Deployment Proof + Remote Smoke
# Canonical executor: Claude Code (recommended) or Terminal.
# No guessing. Atomic writes. Evidence ZIP + SHA. Commit + push.
# ============================================================

REPO_ROOT="/Users/waheebmahmoud/dev/petcare-evidence-repository/petcare_execution"
cd "${REPO_ROOT}" || { echo "FATAL: missing REPO_ROOT=${REPO_ROOT}"; exit 2; }

PHASE="PETCARE-PH-L7-CLOSURE"
TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PHASE}"
OUT="${OUT_ROOT}/${TS_UTC}"
mkdir -p "${OUT}/logs" "${OUT}/snapshots"

echo "=============================================="
echo "PetCare PH-L7 CLOSURE PACK"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "=============================================="

echo ""
echo "=== STEP 0: BASELINE CHECK (NO GUESSING) ==="
need=(
  "scripts/petcare_ci_gates.sh"
  "scripts/petcare_release_integrity_check.sh"
)
missing=0
for f in "${need[@]}"; do
  if [ ! -f "${f}" ]; then echo "MISSING_REQUIRED_FILE=${f}"; missing=1; fi
done
if [ "${missing}" -ne 0 ]; then
  echo "FATAL: missing required baseline files. Stop."
  exit 3
fi

mkdir -p "docs" "scripts"

echo ""
echo "=== STEP 1: WRITE PH-L7 FILES (tmp→mv) ==="

# docs/DEPLOYMENT_PROOF.md
TMP="$(mktemp)"
cat > "${TMP}" <<'MD'
# Deployment Proof — PetCare (PH-L7)

**Document ID:** PETCARE-DEPLOY-PROOF-v1
**Owner:** Platform Ops
**Last Updated (UTC):** 2026-03-03

## Goal
Prove that a deployed runtime satisfies the PH-L6 health contract:

- `GET /health` → 200 + JSON `{status:"ok", ts_utc, ...}`
- `GET /ready` → 200 + JSON `{status:"ready", deps:{...}, ts_utc}`

## Evidence captured (PH-L7 closure pack)
- DNS resolution (hostname → IPs)
- `curl -v` TLS + headers evidence for `/health` and `/ready`
- timing metrics (namelookup/connect/appconnect/starttransfer/total)
- contract validation (JSON schema checks)

## Operator input (no guessing)
PH-L7 requires:

- `PETCARE_BASE_URL="https://<your-domain>"`

Example:
- `PETCARE_BASE_URL="https://api.petcare.sa"`
MD
chmod 0644 "${TMP}"
mv -f "${TMP}" "docs/DEPLOYMENT_PROOF.md"

# scripts/petcare_remote_smoke.sh
TMP="$(mktemp)"
cat > "${TMP}" <<'BASH'
#!/usr/bin/env bash
set -euo pipefail

PETCARE_BASE_URL="${PETCARE_BASE_URL:-}"
if [ -z "${PETCARE_BASE_URL}" ]; then
  echo "FATAL: PETCARE_BASE_URL not set (no guessing). Example: https://api.example.com"
  exit 71
fi

SMOKE_RETRIES="${SMOKE_RETRIES:-5}"
SMOKE_SLEEP_SECONDS="${SMOKE_SLEEP_SECONDS:-2}"
SMOKE_MAX_TOTAL_SECONDS="${SMOKE_MAX_TOTAL_SECONDS:-12}"
SMOKE_MAX_CONNECT_SECONDS="${SMOKE_MAX_CONNECT_SECONDS:-5}"
SMOKE_USER_AGENT="${SMOKE_USER_AGENT:-petcare-remote-smoke/1.0}"
OUT_DIR="${OUT_DIR:-}"

BASE="${PETCARE_BASE_URL%/}"
HEALTH_URL="${BASE}/health"
READY_URL="${BASE}/ready"

host="$(python3 - <<PY
from urllib.parse import urlparse
u=urlparse("${BASE}")
if not u.scheme or not u.netloc:
  raise SystemExit(1)
print(u.hostname or "")
PY
)" || { echo "FATAL: could not parse PETCARE_BASE_URL"; exit 72; }

if [ -z "${host}" ]; then
  echo "FATAL: could not parse hostname from PETCARE_BASE_URL"
  exit 73
fi

echo "=== PH-L7 REMOTE SMOKE ==="
echo "base_url=${BASE}"
echo "host=${host}"
echo "health_url=${HEALTH_URL}"
echo "ready_url=${READY_URL}"
echo "retries=${SMOKE_RETRIES}"
echo "sleep_seconds=${SMOKE_SLEEP_SECONDS}"
echo "max_total_seconds=${SMOKE_MAX_TOTAL_SECONDS}"
echo "max_connect_seconds=${SMOKE_MAX_CONNECT_SECONDS}"
echo ""

echo "=== DNS RESOLUTION (python) ==="
python3 - <<PY
import socket
host="${host}"
infos=socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
addrs=sorted(set(i[4][0] for i in infos))
print("resolved_addrs_count="+str(len(addrs)))
for a in addrs:
  print("addr="+a)
PY

curl_req () {
  local url="$1"
  local name="$2"

  local tmp_body tmp_v metrics
  tmp_body="$(mktemp)"
  tmp_v="$(mktemp)"
  metrics="$(mktemp)"

  set +e
  curl -f -sS -v \
    --connect-timeout "${SMOKE_MAX_CONNECT_SECONDS}" \
    --max-time "${SMOKE_MAX_TOTAL_SECONDS}" \
    -H "User-Agent: ${SMOKE_USER_AGENT}" \
    -o "${tmp_body}" \
    -w $'http_code=%{http_code}\nremote_ip=%{remote_ip}\ntime_namelookup=%{time_namelookup}\ntime_connect=%{time_connect}\ntime_appconnect=%{time_appconnect}\ntime_starttransfer=%{time_starttransfer}\ntime_total=%{time_total}\n' \
    "${url}" \
    2> "${tmp_v}" > "${metrics}"
  rc=$?
  set -e

  if [ -n "${OUT_DIR}" ]; then
    mkdir -p "${OUT_DIR}"
    cp -f "${tmp_body}" "${OUT_DIR}/${name}.body.json" || true
    cp -f "${tmp_v}" "${OUT_DIR}/${name}.curl_verbose.log" || true
    cp -f "${metrics}" "${OUT_DIR}/${name}.curl_metrics.txt" || true
  fi

  if [ "${rc}" -ne 0 ]; then
    echo "FAIL ${name}: curl rc=${rc}"
    sed -n '1,80p' "${tmp_v}" || true
    cat "${metrics}" || true
    rm -f "${tmp_body}" "${tmp_v}" "${metrics}"
    return 1
  fi

  code="$(grep '^http_code=' "${metrics}" | cut -d= -f2)"
  if [ "${code}" != "200" ]; then
    echo "FAIL ${name}: http_code=${code} (expected 200)"
    sed -n '1,80p' "${tmp_body}" || true
    rm -f "${tmp_body}" "${tmp_v}" "${metrics}"
    return 2
  fi

  python3 - <<PY
import json
p="${tmp_body}"
o=json.load(open(p,"r",encoding="utf-8"))
name="${name}"
if name=="health":
  if o.get("status")!="ok": raise SystemExit("FATAL: /health status != ok")
  if "ts_utc" not in o: raise SystemExit("FATAL: /health missing ts_utc")
elif name=="ready":
  if o.get("status")!="ready": raise SystemExit("FATAL: /ready status != ready")
  if "deps" not in o or not isinstance(o["deps"], dict): raise SystemExit("FATAL: /ready missing deps dict")
  if "ts_utc" not in o: raise SystemExit("FATAL: /ready missing ts_utc")
else:
  raise SystemExit("FATAL: unknown name")
print("OK contract validate PASS for "+name)
PY

  echo "OK ${name}: http_code=200"
  cat "${metrics}"
  echo ""

  rm -f "${tmp_body}" "${tmp_v}" "${metrics}"
  return 0
}

attempt=1
while [ "${attempt}" -le "${SMOKE_RETRIES}" ]; do
  echo "=== ATTEMPT ${attempt}/${SMOKE_RETRIES} ==="

  ok=1
  if ! curl_req "${HEALTH_URL}" "health"; then ok=0; fi
  if ! curl_req "${READY_URL}" "ready"; then ok=0; fi

  if [ "${ok}" -eq 1 ]; then
    echo "OK PH-L7 REMOTE SMOKE PASS"
    exit 0
  fi

  if [ "${attempt}" -lt "${SMOKE_RETRIES}" ]; then
    echo "Retrying in ${SMOKE_SLEEP_SECONDS}s..."
    sleep "${SMOKE_SLEEP_SECONDS}"
  fi

  attempt=$((attempt+1))
done

echo "FATAL: PH-L7 REMOTE SMOKE FAIL after ${SMOKE_RETRIES} attempts"
exit 74
BASH
chmod +x "${TMP}"
mv -f "${TMP}" "scripts/petcare_remote_smoke.sh"

# scripts/petcare_deployment_proof_guard.sh
TMP="$(mktemp)"
cat > "${TMP}" <<'BASH'
#!/usr/bin/env bash
set -euo pipefail

need=(
  "scripts/petcare_remote_smoke.sh"
)

missing=0
for f in "${need[@]}"; do
  if [ ! -f "${f}" ]; then
    echo "MISSING_REQUIRED_FILE=${f}"
    missing=1
  fi
done

if [ "${missing}" -ne 0 ]; then
  echo "FATAL: PH-L7 deployment proof surface missing"
  exit 75
fi

echo "OK PH-L7 deployment proof guard PASS"
BASH
chmod +x "${TMP}"
mv -f "${TMP}" "scripts/petcare_deployment_proof_guard.sh"

echo ""
echo "=== STEP 2: RUN DEPLOYMENT PROOF GUARD (MUST PASS) ==="
bash "scripts/petcare_deployment_proof_guard.sh" | tee "${OUT}/logs/deployment_proof_guard.log"

echo ""
echo "=== STEP 3: REMOTE SMOKE (NO GUESSING) ==="
# REQUIRE PETCARE_BASE_URL at runtime.
OUT_DIR="${OUT}/logs/remote_smoke" PETCARE_BASE_URL="${PETCARE_BASE_URL:-}" \
  bash "scripts/petcare_remote_smoke.sh" | tee "${OUT}/logs/remote_smoke.log"

echo ""
echo "=== STEP 4: RELEASE INTEGRITY + CI GATES (MUST PASS) ==="
bash "scripts/petcare_release_integrity_check.sh" | tee "${OUT}/logs/release_integrity.log"
bash "scripts/petcare_ci_gates.sh" | tee "${OUT}/logs/ci_gates.log"

echo ""
echo "=== STEP 5: SNAPSHOT FILES ==="
snap=(
  "docs/DEPLOYMENT_PROOF.md"
  "scripts/petcare_remote_smoke.sh"
  "scripts/petcare_deployment_proof_guard.sh"
)
for f in "${snap[@]}"; do
  mkdir -p "${OUT}/snapshots/$(dirname "${f}")"
  cp -p "${f}" "${OUT}/snapshots/${f}"
done

echo ""
echo "=== STEP 6: MANIFEST + SHA ==="
python3 - <<PY
import json
from pathlib import Path
out=Path("${OUT}")
files=[str(p.relative_to(out)) for p in sorted(out.rglob("*")) if p.is_file()]
m={"phase":"${PHASE}","timestamp_utc":"${TS_UTC}","file_count":len(files),"files":files}
(out/"MANIFEST.json").write_text(json.dumps(m,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("OK wrote MANIFEST.json")
PY

(
  cd "${OUT}" || exit 1
  find . -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 > "closure_sha256.txt"
)

echo ""
echo "=== STEP 7: ZIP + ZIP.SHA256 ==="
mkdir -p "${OUT_ROOT}"
ZIP="${OUT_ROOT}/${PHASE}_${TS_UTC}.zip"
rm -f "${ZIP}" "${ZIP}.sha256"
(
  cd "${OUT_ROOT}" || exit 1
  zip -r "${PHASE}_${TS_UTC}.zip" "${TS_UTC}" >/dev/null
  shasum -a 256 "${PHASE}_${TS_UTC}.zip" > "${PHASE}_${TS_UTC}.zip.sha256"
)

echo ""
echo "=== STEP 8: COMMIT / PUSH ==="
git status -sb | tee "${OUT}/logs/git_status.log"

git add \
  "docs/DEPLOYMENT_PROOF.md" \
  "scripts/petcare_remote_smoke.sh" \
  "scripts/petcare_deployment_proof_guard.sh" \
  "scripts/petcare_ph_l7_closure_pack.sh"

git commit -m "PH-L7: deployment proof + remote smoke"
git push origin main

echo ""
echo "DONE"
echo "ZIP=${ZIP}"
echo "ZIP_SHA=${ZIP}.sha256"
echo "COMMIT=$(git rev-parse HEAD)"
