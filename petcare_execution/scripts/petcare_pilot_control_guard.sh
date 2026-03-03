#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CTL="${REPO_ROOT}/FND/PILOT_CONTROL.json"

if [ ! -f "${CTL}" ]; then
  echo "FATAL: missing FND/PILOT_CONTROL.json"
  exit 50
fi

python3 - <<PY
import json,sys,os
p="${CTL}"
o=json.load(open(p,"r",encoding="utf-8"))
if o.get("schema")!="petcare.pilot_control.v1": raise SystemExit("FATAL: bad schema")
if o.get("schema_version")!=1: raise SystemExit("FATAL: bad schema_version")
pe=o.get("pilot_enabled")
if pe not in (True,False): raise SystemExit("FATAL: pilot_enabled must be boolean")
req=o.get("activation_requires_ceo_declaration")
if req not in (True,False): raise SystemExit("FATAL: activation_requires_ceo_declaration must be boolean")
decl=o.get("ceo_declaration_path")
if not isinstance(decl,str) or not decl: raise SystemExit("FATAL: ceo_declaration_path missing")
print("pilot_enabled="+str(pe).lower())
print("activation_requires_ceo_declaration="+str(req).lower())
print("ceo_declaration_path="+decl)
PY

PILOT_ENABLED="$(python3 - <<PY
import json
o=json.load(open("${CTL}","r",encoding="utf-8"))
print("true" if o["pilot_enabled"] else "false")
PY
)"

REQ_DECL="$(python3 - <<PY
import json
o=json.load(open("${CTL}","r",encoding="utf-8"))
print("true" if o["activation_requires_ceo_declaration"] else "false")
PY
)"

DECL_PATH="$(python3 - <<PY
import json
o=json.load(open("${CTL}","r",encoding="utf-8"))
print(o["ceo_declaration_path"])
PY
)"

# If pilot is enabled, require CEO declaration file to exist AND be filled (not template-only).
if [ "${PILOT_ENABLED}" = "true" ] && [ "${REQ_DECL}" = "true" ]; then
  if [ ! -f "${REPO_ROOT}/${DECL_PATH}" ]; then
    echo "FATAL: pilot_enabled=true but missing CEO declaration at ${DECL_PATH}"
    exit 51
  fi
  # Require at least one checkbox selection and signature date filled.
  if ! grep -qE '^\- \[x\] \*\*GO\*\*|^\- \[x\] \*\*NO-GO\*\*' "${REPO_ROOT}/${DECL_PATH}"; then
    echo "FATAL: CEO declaration not completed (GO/NO-GO not selected)"
    exit 52
  fi
  if grep -qE 'Date \(UTC\):[[:space:]]*_+' "${REPO_ROOT}/${DECL_PATH}"; then
    echo "FATAL: CEO declaration date appears unfilled"
    exit 53
  fi
  if grep -qE 'Signature:[[:space:]]*_+' "${REPO_ROOT}/${DECL_PATH}"; then
    echo "FATAL: CEO declaration signature appears unfilled"
    exit 54
  fi
  echo "OK: pilot enabled and CEO declaration appears completed"
  exit 0
fi

echo "OK: pilot control guard PASS (pilot not enabled, or CEO declaration not required)"
