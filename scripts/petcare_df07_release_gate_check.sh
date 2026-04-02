#!/usr/bin/env bash
set -euo pipefail

required_vars=(
  PETCARE_RELEASE_COMMIT
  PETCARE_ARTIFACT_DIGEST
  PETCARE_RELEASE_APPROVER
  PETCARE_DEPLOY_OPERATOR
  PETCARE_ROLLBACK_TARGET
  PETCARE_NONPROD_SERVICE_URL
  PETCARE_PROD_SERVICE_URL
  PETCARE_EVIDENCE_ROOT
)

fail() {
  echo "DF07_RELEASE_GATE_CHECK: FAIL - $1" >&2
  exit 1
}

for var_name in "${required_vars[@]}"; do
  if [ -z "${!var_name:-}" ]; then
    fail "missing required variable ${var_name}"
  fi
done

case "${PETCARE_ARTIFACT_DIGEST}" in
  *:latest|latest)
    fail "artifact digest must not use latest"
    ;;
esac

case "${PETCARE_ARTIFACT_DIGEST}" in
  sha256:*|*@sha256:*)
    ;;
  *)
    fail "artifact digest must be immutable digest form"
    ;;
esac

if ! printf '%s' "${PETCARE_RELEASE_COMMIT}" | grep -Eq '^[0-9a-f]{7,40}$'; then
  fail "release commit must look like a git commit hash"
fi

if [ "${PETCARE_NONPROD_SERVICE_URL}" = "${PETCARE_PROD_SERVICE_URL}" ]; then
  fail "nonprod and prod service URLs must differ"
fi

case "${PETCARE_EVIDENCE_ROOT}" in
  *petcare_execution/EVIDENCE*)
    ;;
  *)
    fail "evidence root must point into petcare_execution/EVIDENCE"
    ;;
esac

echo "DF07_RELEASE_GATE_CHECK: PASS"
echo "release_commit=${PETCARE_RELEASE_COMMIT}"
echo "artifact_digest=${PETCARE_ARTIFACT_DIGEST}"
echo "release_approver=${PETCARE_RELEASE_APPROVER}"
echo "deploy_operator=${PETCARE_DEPLOY_OPERATOR}"
echo "rollback_target=${PETCARE_ROLLBACK_TARGET}"
echo "nonprod_service_url=${PETCARE_NONPROD_SERVICE_URL}"
echo "prod_service_url=${PETCARE_PROD_SERVICE_URL}"
echo "evidence_root=${PETCARE_EVIDENCE_ROOT}"
