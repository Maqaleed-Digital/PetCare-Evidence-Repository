PETCARE DF06
Production Access Model

Principle
Production is private-by-default and least-privilege-by-default.

Access Layers
1. Deploy access
2. Runtime service identity
3. Operator access
4. Diagnostic access
5. Emergency access

Rules
Deploy access is restricted to approved deploy authority only
Runtime identity is prod-only and cannot be shared
Operator access is role-based and logged
Diagnostic access is time-bound and approved
Emergency access is break-glass, justified, and logged

Public Exposure Rule
No unauthenticated public production exposure unless explicitly approved in writing and supported by monitoring, WAF or equivalent edge control, and rollback readiness.

Identity Separation
Prod identities must be different from nonprod
Prod secrets must be different from nonprod
Prod configuration must be different from nonprod where required by environment

Audit Requirement
Every material access change must be traceable by actor, timestamp, purpose, and environment.

Blocked Conditions
Shared identity across environments
Undocumented break-glass access
Missing auditability for prod access
