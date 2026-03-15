# Control Propagation Verification

Verified Shared Controls
- identity_rbac propagation
- audit_ledger propagation
- consent_registry propagation
- clinical_signoff propagation where clinical completion and immutability apply
- evidence_export governance presence at platform level

Propagation Result
PASS

Propagation Notes
- identity_rbac is consumed in all authoritative runtime layers
- audit_ledger is consumed in all authoritative runtime layers
- consent_registry appears in privacy-aware boundaries including records, document/media, emergency packet preparation, and AI intake
- clinical_signoff is integrated into consultation completion through sign-off hookup
- evidence_export remains the governed export boundary for evidence generation processes

Propagation Rule
A shared control passes only if it appears in all runtime layers where the governed behavior actually applies.
