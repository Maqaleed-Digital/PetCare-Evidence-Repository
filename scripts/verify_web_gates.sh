#!/usr/bin/env bash
set -euo pipefail

: "${SERVICE_URL:?Missing SERVICE_URL}"
: "${API_BASE_URL:?Missing API_BASE_URL}"
: "${AUDIT_PROBE_ENDPOINT:?Missing AUDIT_PROBE_ENDPOINT}"
: "${DOMAIN_VERIFIED:?Missing DOMAIN_VERIFIED}"
: "${DNS_RR_APPLIED:?Missing DNS_RR_APPLIED}"
: "${DOMAIN_GO_LIVE_APPROVED:?Missing DOMAIN_GO_LIVE_APPROVED}"

curl -fsS "${SERVICE_URL%/}/api/health" >/dev/null
curl -fsS "${API_BASE_URL%/}/health" >/dev/null
curl -fsS -X POST "$AUDIT_PROBE_ENDPOINT" \
  -H 'content-type: application/json' \
  -d '{"event_name":"ui.audit.probe","actor_role":"admin","surface":"postdeploy","correlation_id":"gate-check"}' >/dev/null

if [[ "$DOMAIN_VERIFIED" != "true" ]]; then
  echo "Domain verification missing"
  exit 1
fi

if [[ "$DNS_RR_APPLIED" != "true" ]]; then
  echo "DNS records not confirmed"
  exit 1
fi

if [[ "$DOMAIN_GO_LIVE_APPROVED" != "true" ]]; then
  echo "Domain go-live approval missing"
  exit 1
fi

echo "Web gates passed"
