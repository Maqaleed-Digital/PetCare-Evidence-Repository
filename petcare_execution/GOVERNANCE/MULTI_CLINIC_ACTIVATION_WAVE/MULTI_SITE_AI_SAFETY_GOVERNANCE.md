# MULTI-SITE AI SAFETY GOVERNANCE

## Purpose
This document extends the approved assistive AI boundary from a single live clinic to a governed multi-site network.

## Non-negotiable boundary
The AI runtime remains assistive only across all sites.

The following remain mandatory:

- no autonomous diagnosis
- no autonomous prescribing
- no autonomous emergency disposition
- no autonomous medication release
- no removal of clinician approval
- no removal of pharmacist review where required
- no bypass of escalation controls
- no silent model behavior change at site level

## Multi-site control requirements
Every clinic must inherit the same base AI policy contract.

Per-site variation is limited to:
- site code
- local staffing roster
- local escalation contacts
- local operating windows
- clinic activation state

## Required safety controls
1. Human-in-the-loop preserved at every site
2. Override event logging per site
3. Escalation pathway per site
4. Kill-switch authority per site
5. Central policy consistency across sites
6. Cross-site comparison of override rates
7. Hypercare observation for newly activated sites
8. Portfolio-level review of safety deviations

## Activation rule
A site cannot enter active operation unless all eight controls above are positively attested in governance evidence.

## Drift rule
If a site drifts from the approved AI boundary, that site is returned to controlled remediation or paused from active AI-assisted operation.
