#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POSTURE="${REPO_ROOT}/FND/PAYMENT_POSTURE.json"

if [ ! -f "${POSTURE}" ]; then
  echo "FATAL: missing FND/PAYMENT_POSTURE.json"
  exit 40
fi

# parse via python to avoid jq dependency
python3 - <<PY
import json,sys
p="${POSTURE}"
o=json.load(open(p,"r",encoding="utf-8"))
if o.get("schema")!="petcare.payment_posture.v1": raise SystemExit("FATAL: bad schema")
if o.get("schema_version")!=1: raise SystemExit("FATAL: bad schema_version")
pe=o.get("payments_enabled")
if pe not in (True,False): raise SystemExit("FATAL: payments_enabled must be boolean")
print("payments_enabled="+str(pe).lower())
print("payment_provider="+str(o.get("payment_provider")))
PY

PAYMENTS_ENABLED="$(python3 - <<PY
import json
o=json.load(open("${POSTURE}","r",encoding="utf-8"))
print("true" if o["payments_enabled"] else "false")
PY
)"

# Heuristic keywords that should not appear if payments are disabled.
# No guessing: keep narrow and high-signal.
PAYMENT_NEEDLES=(
  "STRIPE_"
  "TAP_"
  "HYPERPAY_"
  "PAYMENT_PROVIDER"
  "CHECKOUT_SESSION"
  "PAYMENT_INTENT"
)

if [ "${PAYMENTS_ENABLED}" = "false" ]; then
  # Fail if tracked files contain strong payment-provider configuration references.
  # Exclude docs/ because this pack introduces compliance docs that may mention the word "payment".
  for n in "${PAYMENT_NEEDLES[@]}"; do
    if git grep -n -- "${n}" -- . ":(exclude)docs" >/dev/null 2>&1; then
      echo "FATAL: payments disabled but found payment configuration reference: ${n}"
      git grep -n -- "${n}" -- . ":(exclude)docs" | head -n 20 || true
      exit 41
    fi
  done
  echo "OK: payment posture guard PASS (payments disabled; no provider refs found)"
  exit 0
fi

# payments enabled path: require provider declaration (non-secret)
python3 - <<PY
import json,sys
o=json.load(open("${POSTURE}","r",encoding="utf-8"))
if not o.get("payment_provider"):
  raise SystemExit("FATAL: payments_enabled=true requires payment_provider non-null")
print("OK: payments enabled posture has provider="+str(o["payment_provider"]))
PY

echo "OK: payment posture guard PASS (payments enabled posture valid)"
