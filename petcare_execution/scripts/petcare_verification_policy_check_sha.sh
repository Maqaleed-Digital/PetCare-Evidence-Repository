#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

PROD_ZIP_SHA256="${1:-}"
INDEX="${2:-FND/VERIFICATION_INDEX.json}"

if [ -z "${PROD_ZIP_SHA256}" ]; then
  echo "ERROR: missing arg1 PROD_ZIP_SHA256"
  echo "USAGE: scripts/petcare_verification_policy_check_sha.sh <PROD_ZIP_SHA256> [INDEX_JSON]"
  exit 2
fi

if [ ! -f "${INDEX}" ]; then
  echo "ERROR: index not found: ${INDEX}"
  exit 3
fi

python3 - <<'PY' "${INDEX}" "${PROD_ZIP_SHA256}"
import json, sys
idx_path=sys.argv[1]
want=sys.argv[2]
idx=json.load(open(idx_path,"r",encoding="utf-8"))
entries=idx.get("entries") or []
hits=[e for e in entries if e.get("verified_zip_sha256")==want and e.get("overall_pass")=="true"]
if not hits:
    print("POLICY_FAIL")
    print("verified_zip_sha256=" + want)
    raise SystemExit(10)
e=hits[-1]
print("POLICY_PASS")
print("verified_zip_sha256=" + want)
print("entry_hash=" + (e.get("entry_hash") or ""))
print("verifier_pack=" + (e.get("verifier_pack") or ""))
print("verifier_zip_sha256=" + (e.get("verifier_zip_sha256") or ""))
PY
