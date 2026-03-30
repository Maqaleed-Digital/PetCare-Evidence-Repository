# PETCARE — EP-09 HARD GATES

## G-F6 Invoice Lifecycle Integrity
- invoice states explicitly defined
- only permitted transitions allowed
- all transitions logged
- closed invoices cannot silently reopen

## G-F7 Reconciliation Resolution Control
- mismatch detection separate from mismatch resolution
- no auto-resolution allowed
- reviewer identity and timestamp required for any resolution

## G-F8 Dispute Governance Gate
- dispute initiation recorded
- dispute evidence linked
- resolution reason required
- no silent dispute closure

## G-F9 Financial Visibility Accuracy
- statement totals derived deterministically
- aging derived from stable timestamps
- exposure view traceable to source records

## G-F10 External Signal Handling Gate
- external statuses are recorded, not blindly trusted
- external signals cannot bypass human review where required
- external callbacks cannot autonomously enable payment execution

## Pass Conditions
- tests pass
- evidence pack generated
- manifest generated
- working tree committed and pushed
