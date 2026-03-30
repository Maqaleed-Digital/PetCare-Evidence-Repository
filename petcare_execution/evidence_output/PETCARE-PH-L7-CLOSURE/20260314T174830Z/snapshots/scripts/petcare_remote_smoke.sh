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
