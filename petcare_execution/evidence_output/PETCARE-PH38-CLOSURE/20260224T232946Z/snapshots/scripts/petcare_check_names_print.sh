#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO}"

CI_WF=".github/workflows/ci.yml"
REQ_WF=".github/workflows/required_checks.yml"

echo "=== REQUIRED STATUS CHECK NAMES (BRANCH PROTECTION) ==="
echo "repo=${REPO}"

if [ ! -f "${CI_WF}" ]; then
  echo "FAIL: missing ${CI_WF}"
  exit 10
fi
if [ ! -f "${REQ_WF}" ]; then
  echo "FAIL: missing ${REQ_WF}"
  exit 11
fi

ci_name="$(awk '/^name:/{print $2; exit}' "${CI_WF}" | tr -d '[:space:]')"
req_name="$(awk '/^name:/{print $2; exit}' "${REQ_WF}" | tr -d '[:space:]')"

if [ -z "${ci_name}" ]; then
  echo "FAIL: could not parse workflow name from ${CI_WF}"
  exit 12
fi
if [ -z "${req_name}" ]; then
  echo "FAIL: could not parse workflow name from ${REQ_WF}"
  exit 13
fi

# Job ids are the YAML keys under "jobs:"
ci_job="$(awk '
  $0 ~ /^jobs:/ {in_jobs=1; next}
  in_jobs==1 && $0 ~ /^[[:space:]]{2}[A-Za-z0-9_-]+:/ {gsub(":","",$1); print $1; exit}
' "${CI_WF}" | tr -d '[:space:]')"

req_job="$(awk '
  $0 ~ /^jobs:/ {in_jobs=1; next}
  in_jobs==1 && $0 ~ /^[[:space:]]{2}[A-Za-z0-9_-]+:/ {gsub(":","",$1); print $1; exit}
' "${REQ_WF}" | tr -d '[:space:]')"

if [ -z "${ci_job}" ]; then
  echo "FAIL: could not parse first job id from ${CI_WF}"
  exit 14
fi
if [ -z "${req_job}" ]; then
  echo "FAIL: could not parse first job id from ${REQ_WF}"
  exit 15
fi

echo ""
echo "ADD THESE IN GITHUB BRANCH PROTECTION > Required status checks:"
echo "  - ${ci_name} / ${ci_job}"
echo "  - ${req_name} / ${req_job}"
echo ""
echo "RESULT=PASS"
exit 0
