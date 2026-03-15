# admin-service Runtime Module

Purpose
Clinic operational administration service.

Owns
- clinic configuration
- staff management
- scheduling configuration
- operational reporting

Consumes
- identity_rbac admin role evaluation
- audit_ledger logging

Produces
- clinic operational events
- scheduling changes

Does Not Own
- clinical records
- pharmacy dispensing
