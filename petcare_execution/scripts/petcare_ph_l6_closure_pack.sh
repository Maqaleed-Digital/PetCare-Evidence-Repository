#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# PH-L6 — Runtime Smoke + Health Surface
# Canonical executor: Claude Code or Terminal (file-based).
# No guessing. Atomic writes. Evidence ZIP + SHA. Commit + push.
# ============================================================

REPO_ROOT="/Users/waheebmahmoud/dev/petcare-evidence-repository/petcare_execution"
cd "${REPO_ROOT}" || { echo "FATAL: missing REPO_ROOT=${REPO_ROOT}"; exit 2; }

PHASE="PETCARE-PH-L6-CLOSURE"
TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PHASE}"
OUT="${OUT_ROOT}/${TS_UTC}"
mkdir -p "${OUT}/logs" "${OUT}/snapshots"

echo "=============================================="
echo "PetCare PH-L6 CLOSURE PACK"
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
  if [ ! -f "${f}" ]; then
    echo "MISSING_REQUIRED_FILE=${f}"
    missing=1
  fi
done
if [ "${missing}" -ne 0 ]; then
  echo "FATAL: missing required baseline files. Stop."
  exit 3
fi

mkdir -p "docs" "scripts"

echo ""
echo "=== STEP 1: WRITE RUNTIME HEALTH CONTRACT (tmp→mv) ==="
TMP="$(mktemp)"
cat > "${TMP}" <<'MD'
# Runtime Health Contract — PetCare (PH-L6)

**Document ID:** PETCARE-RUNTIME-HEALTH-v1
**Owner:** Platform Ops
**Last Updated (UTC):** 2026-03-03

## Endpoints (minimum)

### 1) GET /health
Purpose: Liveness — process is up and can serve requests.

Response (200):

{
  "status": "ok",
  "service": "petcare",
  "ts_utc": "20260303T000000Z",
  "version": "dev"
}

### 2) GET /ready
Purpose: Readiness — service is ready to accept traffic.

Response (200):

{
  "status": "ready",
  "deps": {
    "db": "unknown",
    "queue": "unknown"
  },
  "ts_utc": "20260303T000000Z"
}

Failure semantics:
- /health non-200 → process unhealthy
- /ready non-200 → dependency not ready

Governance note:
PH-L6 introduces a reference local health server + smoke harness.
Production systems must mirror this contract.
MD
chmod 0644 "${TMP}"
mv -f "${TMP}" "docs/RUNTIME_HEALTH_CONTRACT.md"

echo ""
echo "=== STEP 2: WRITE LOCAL HEALTH SERVER ==="
TMP="$(mktemp)"
cat > "${TMP}" <<'PY'
#!/usr/bin/env python3
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone

def ts():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

SERVICE = os.environ.get("PETCARE_SERVICE", "petcare")
VERSION = os.environ.get("PETCARE_VERSION", "dev")

class Handler(BaseHTTPRequestHandler):
    def send_json(self, code, payload):
        body = (json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + "\n").encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self.send_json(200, {
                "status": "ok",
                "service": SERVICE,
                "ts_utc": ts(),
                "version": VERSION
            })
            return
        if self.path == "/ready":
            self.send_json(200, {
                "status": "ready",
                "deps": {"db": "unknown", "queue": "unknown"},
                "ts_utc": ts()
            })
            return
        self.send_json(404, {"status": "not_found", "ts_utc": ts()})

    def log_message(self, format, *args):
        return

def main():
    host = "127.0.0.1"
    port = 8099
    server = HTTPServer((host, port), Handler)
    print(f"Health server listening on {host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    main()
PY
chmod +x "${TMP}"
mv -f "${TMP}" "scripts/petcare_health_server.py"

echo ""
echo "=== STEP 3: WRITE RUNTIME SMOKE SCRIPT ==="
TMP="$(mktemp)"
cat > "${TMP}" <<'BASH'
#!/usr/bin/env bash
set -euo pipefail

HEALTH_URL="${HEALTH_URL:-}"
if [ -z "${HEALTH_URL}" ]; then
  echo "FATAL: HEALTH_URL not set"
  exit 61
fi

READY_URL="${HEALTH_URL%/health}/ready"

H="$(curl -fsS "${HEALTH_URL}")" || { echo "FATAL: health failed"; exit 62; }
R="$(curl -fsS "${READY_URL}")" || { echo "FATAL: ready failed"; exit 63; }

python3 - <<PY
import json
h=json.loads("""${H}""")
r=json.loads("""${R}""")
assert h["status"]=="ok"
assert r["status"]=="ready"
print("OK runtime smoke PASS")
PY
BASH
chmod +x "${TMP}"
mv -f "${TMP}" "scripts/petcare_runtime_smoke.sh"

echo ""
echo "=== STEP 4: WRITE CI SURFACE GUARD ==="
TMP="$(mktemp)"
cat > "${TMP}" <<'BASH'
#!/usr/bin/env bash
set -euo pipefail

need=(
  "docs/RUNTIME_HEALTH_CONTRACT.md"
  "scripts/petcare_health_server.py"
  "scripts/petcare_runtime_smoke.sh"
)

missing=0
for f in "${need[@]}"; do
  if [ ! -f "${f}" ]; then
    echo "MISSING_REQUIRED_FILE=${f}"
    missing=1
  fi
done

if [ "${missing}" -ne 0 ]; then
  echo "FATAL: PH-L6 surface missing"
  exit 66
fi

echo "OK PH-L6 surface guard PASS"
BASH
chmod +x "${TMP}"
mv -f "${TMP}" "scripts/petcare_runtime_smoke_guard.sh"

echo ""
echo "=== STEP 5: LOCAL SMOKE TEST ==="

python3 scripts/petcare_health_server.py >"${OUT}/logs/server.log" 2>&1 &
PID=$!
sleep 0.5

set +e
HEALTH_URL="http://127.0.0.1:8099/health" bash scripts/petcare_runtime_smoke.sh | tee "${OUT}/logs/smoke.log"
RC=$?
set -e

kill "${PID}" >/dev/null 2>&1 || true

if [ "${RC}" -ne 0 ]; then
  echo "FATAL: runtime smoke failed"
  exit 6
fi

echo ""
echo "=== STEP 6: RELEASE INTEGRITY + CI GATES ==="
bash scripts/petcare_release_integrity_check.sh | tee "${OUT}/logs/release_integrity.log"
bash scripts/petcare_ci_gates.sh | tee "${OUT}/logs/ci_gates.log"

echo ""
echo "=== STEP 7: SNAPSHOT FILES ==="
snap=(
  "docs/RUNTIME_HEALTH_CONTRACT.md"
  "scripts/petcare_health_server.py"
  "scripts/petcare_runtime_smoke.sh"
  "scripts/petcare_runtime_smoke_guard.sh"
)
for f in "${snap[@]}"; do
  mkdir -p "${OUT}/snapshots/$(dirname "${f}")"
  cp -p "${f}" "${OUT}/snapshots/${f}"
done

echo ""
echo "=== STEP 8: MANIFEST + SHA ==="
python3 - <<PY
import json
from pathlib import Path
out=Path("${OUT}")
files=[str(p.relative_to(out)) for p in sorted(out.rglob("*")) if p.is_file()]
m={"phase":"${PHASE}","timestamp_utc":"${TS_UTC}","file_count":len(files),"files":files}
(out/"MANIFEST.json").write_text(json.dumps(m,indent=2)+"\n")
print("OK wrote MANIFEST.json")
PY

(
  cd "${OUT}" || exit 1
  find . -type f -print0 | sort -z | xargs -0 shasum -a 256 > closure_sha256.txt
)

echo ""
echo "=== STEP 9: ZIP ==="
ZIP="${OUT_ROOT}/${PHASE}_${TS_UTC}.zip"
(
  cd "${OUT_ROOT}" || exit 1
  zip -r "${PHASE}_${TS_UTC}.zip" "${TS_UTC}" >/dev/null
  shasum -a 256 "${PHASE}_${TS_UTC}.zip" > "${PHASE}_${TS_UTC}.zip.sha256"
)

echo ""
echo "=== STEP 10: COMMIT / PUSH ==="
git add \
  docs/RUNTIME_HEALTH_CONTRACT.md \
  scripts/petcare_health_server.py \
  scripts/petcare_runtime_smoke.sh \
  scripts/petcare_runtime_smoke_guard.sh

git commit -m "PH-L6: runtime health contract + local smoke surface"
git push origin main

echo ""
echo "DONE"
echo "ZIP=${ZIP}"
echo "ZIP_SHA=${ZIP}.sha256"
echo "COMMIT=$(git rev-parse HEAD)"
