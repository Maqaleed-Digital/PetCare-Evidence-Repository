DOMAIN GO-LIVE POLICY

The public domain may go live only after:
- deployed UI health endpoint returns 200
- API_BASE_URL/health returns 200
- auth mode, issuer, audience, and session secret are present
- audit probe endpoint accepts a real event payload
- DOMAIN_VERIFIED=true
- DNS_RR_APPLIED=true
- DOMAIN_GO_LIVE_APPROVED=true
