PETCARE-PRODUCTION-INFRASTRUCTURE-DEPLOYMENT
CLOUD_DEPLOYMENT_MODEL

Purpose
Define the governed production cloud deployment model without binding the pack to a single vendor.

Residency Rule
Primary production systems of record, logs, and regulated data must remain KSA-resident by default.

Reference Deployment Shape
- Region: KSA production region only
- Network: isolated VPC/VNet equivalent
- Ingress: controlled public ingress only at edge
- Private workloads: application runtime and database in private subnets
- Outbound control: egress restricted and logged

Logical Zones
1. Edge zone
- WAF
- TLS termination
- API gateway
- ingress load balancer

2. Application zone
- web runtime
- API runtime
- async worker runtime
- workflow runtime

3. Data zone
- PostgreSQL
- object storage
- backup storage
- audit/event storage

4. Operations zone
- metrics
- logs
- traces
- alert manager
- dashboards

5. Security zone
- secrets manager
- key management
- identity federation
- break-glass logging

Scaling Model
Phase 1
- single production cluster or runtime pool
- HA database baseline
- managed storage
- observability on by default

Phase 2
- horizontal app scale
- read replicas
- queue partitioning
- dedicated analytics path

Phase 3
- multi-clinic and regional scale
- workload isolation by domain if needed
- controlled service extraction

Build vs Buy Alignment
Internal control required:
- governance runtime boundaries
- audit evidence model
- clinical and pharmacy trust semantics
- AI logging and approval chain

Can be partner or managed:
- cloud primitives
- observability tooling
- secret storage platform
- WAF and CDN edge services

Release Policy
No infrastructure promotion without:
- validation script pass
- manifest generation
- evidence output present
- commit recorded
