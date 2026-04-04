# PETCARE DF17 — Override Governance Model

## Purpose
Allow controlled temporary overrides to the default scoring weights without governance drift.

## Override Principles
- temporary
- scoped
- explicit
- audited
- reversible

## Override Preconditions
Override is valid only if all are present:
- override_requested = true
- override_justification is defined
- override_scope is defined
- override_approved = true
- override_effective_period is defined

## Required Override Record Fields
- override_id
- requested_by
- approved_by
- reason
- affected_units
- effective_period
- previous_weights
- new_weights
- weights_version
- created_at_utc

## Fail-Closed Rule
If override is present and approval is missing, block execution.

## Scope Rule
Scope may be:
- global
- portfolio_segment
- named_unit

## Expiry Rule
Expired override must not be applied.

## Reversion Rule
On expiry, default locked weights become effective immediately unless a new approved override exists.
