PETCARE-PRODUCTION-HYPERCARE-AND-OPERATIONS-GOVERNANCE
HYPERCARE_OPERATING_WINDOW

Purpose
Define the governed hypercare operating window immediately following verified live production activation.

State Transition
- Current: petcare_live_production_verified
- Target: petcare_hypercare_governed_operations_active

Operating Window
- hypercare_start_utc
- hypercare_end_utc
- daily review cadence
- named business owner
- named operations owner
- named technical owner
- named incident commander rotation

Minimum Hypercare Coverage
- live system health review
- incident review
- backlog of production issues
- deployment and change review
- audit and AI governance path review
- clinic and pharmacy operational stability review

Rules
- hypercare period must be explicitly time-bounded
- daily review evidence is mandatory
- unresolved Sev-1 and Sev-2 issues block hypercare closeout
- emergency changes must follow emergency change rules
- observability and audit paths must remain actively reviewed

Exit Rule
Hypercare closes only when:
- closeout criteria pass
- daily operations are stable
- no blocking production issues remain open
