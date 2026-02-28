#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

ZIP="${1:-}"
INDEX="${2:-FND/VERIFICATION_INDEX.json}"

if [ -z "${ZIP}" ]; then
  echo "ERROR: missing arg1 production zip path"
  echo "USAGE: scripts/petcare_verification_policy_check.sh <PROD_PACK_ZIP> [INDEX_JSON]"
  exit 2
fi

if [ ! -f "${ZIP}" ]; then
  echo "ERROR: zip not found: ${ZIP}"
  exit 3
fi

if [ ! -f "${INDEX}" ]; then
  echo "ERROR: index not found: ${INDEX}"
  exit 4
fi

ZIP_SHA="$(shasum -a 256 "${ZIP}" | awk '{print $1}')"

python3 - <<'PY' "${INDEX}" "${ZIP_SHA}"
import json, sys
idx_path = sys.argv[1]
zip_sha = sys.argv[2]
idx = json.load(open(idx_path, "r", encoding="utf-8"))
entries = idx.get("entries") or []
matches = [e for e in entries if e.get("verified_zip_sha256") == zip_sha and e.get("overall_pass") == "true"]
if not matches:
    print("POLICY_FAIL: production zip is NOT verified in index (or overall_pass != true)")
    print("zip_sha256=" + zip_sha)
    raise SystemExit(10)
# Use most recent match
e = matches[-1]
print("POLICY_PASS")
print("zip_sha256=" + zip_sha)
print("entry_hash=" + (e.get("entry_hash") or ""))
print("verifier_pack=" + (e.get("verifier_pack") or ""))
print("verifier_zip_sha256=" + (e.get("verifier_zip_sha256") or ""))
PY
