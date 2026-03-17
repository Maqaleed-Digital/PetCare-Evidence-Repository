PETCARE-PRODUCTION-INFRASTRUCTURE-DEPLOYMENT
NETWORK_TOPOLOGY

Purpose
Define production network segmentation and trust boundaries.

Topology
- Public edge subnet
- Private application subnet
- Private data subnet
- Restricted operations subnet

Ingress Path
Internet
-> WAF
-> API gateway / ingress load balancer
-> web/API runtime

East-West Path
- only approved runtime-to-runtime communication
- deny by default
- service identity required where supported

Database Access
- database reachable only from application subnet
- no public database endpoint
- admin access through controlled bastion or equivalent audited path only

Object Storage Access
- private-by-default buckets/containers
- scoped runtime identities only
- signed access for temporary document retrieval where required

Observability Access
- app runtimes emit logs, metrics, traces to operations subnet endpoints
- dashboards restricted to authorized admin/ops roles

Secrets Access
- secrets retrieval only from runtime identities
- no plaintext secret storage in repository
- rotation events logged

Partner Integration Pattern
- ingress through gateway only
- partner routes isolated by auth and policy
- request logging mandatory
- rate limits mandatory

Minimum Security Rules
- deny all by default
- explicit allow rules only
- TLS in transit
- subnet-level separation
- audit logging for privileged access

Validation Expectations
- no public database exposure
- no unrestricted internal traffic
- no repository-stored secret values
- no direct bypass around gateway
