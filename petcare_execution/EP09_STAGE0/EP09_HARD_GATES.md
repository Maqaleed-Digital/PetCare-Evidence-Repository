# PETCARE — EP-09 HARD GATES

Status: LOCKED

## G-F6 Invoice Lifecycle Integrity
Requirements:
- invoice states explicitly defined
- only permitted transitions allowed
- all transitions logged
- closed invoices cannot silently reopen

## G-F7 Reconciliation Resolution Control
Requirements:
- mismatch detection separate from mismatch resolution
- no auto-resolution allowed
- reviewer identity and timestamp required for any resolution

## G-F8 Dispute Governance Gate
Requirements:
- dispute initiation recorded
- dispute evidence linked
- resolution reason required
- no silent dispute closure

## G-F9 Financial Visibility Accuracy
Requirements:
- statement totals derived deterministically
- aging derived from stable timestamps
- exposure view traceable to source records

## G-F10 External Signal Handling Gate
Requirements:
- external statuses are recorded, not blindly trusted
- external signals cannot bypass human review where required
- no external callback may autonomously enable payment execution

## Phase 0 Pass Conditions
- architecture lock document created
- dependency map created
- next scope execution spec created
- evidence pack generated
- manifest generated
