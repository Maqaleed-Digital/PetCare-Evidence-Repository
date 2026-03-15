# Blocked Item Resolution Sequence

Status: Resolution order for runtime blockers identified by PH-FND-4

## Known Blocker Categories

1. owner-service
2. vet-service
3. admin-service
4. pharmacy-service
5. emergency-service
6. drug interaction DB
7. clinical service
8. unresolved deferred integrations and domain dependencies

## Resolution Order

### Step 1
Resolve service ownership blockers

Required outputs:
- named owner-service runtime boundary
- named vet-service runtime boundary
- named admin-service runtime boundary
- named pharmacy-service runtime boundary
- named emergency-service runtime boundary

### Step 2
Resolve shared governance dependency binding

Required outputs:
- each surface service mapped to identity_rbac
- each relevant surface mapped to consent_registry
- all services mapped to audit_ledger
- vet and emergency flows mapped to clinical_signoff
- admin and governance flows mapped to evidence_export

### Step 3
Resolve clinical shared service boundary

Required outputs:
- define clinical shared runtime boundary
- define what belongs to UPHR vs consultation vs sign-off
- define prescription handoff checkpoint

### Step 4
Resolve medication safety dependency strategy

Required outputs:
- define interim medication safety realization mode
- define external data dependency posture for interaction checking
- define blocker condition for production safety completeness

### Step 5
Resolve emergency dependency chain

Required outputs:
- define availability source boundary
- define escalation packet minimum data set
- define consent-aware handoff rule

### Step 6
Resolve deferred items as explicit future runtime backlog

Required outputs:
- each deferred item tagged as:
  - runtime prerequisite
  - phase-later enhancement
  - external integration dependency
  - not required for MVP runtime start

## Resolution Rule

A blocker is considered resolved only when:

- boundary owner is named
- predecessor dependency is known
- gate impact is recorded
- implementation start condition is written
