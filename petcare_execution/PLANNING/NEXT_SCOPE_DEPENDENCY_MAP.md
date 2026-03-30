# NEXT SCOPE DEPENDENCY MAP

## Next Epic

EP-06 Emergency Network

## Dependency Summary

EP-06 depends on controlled behavior already delivered in prior epics.

### EP-01 Dependencies

1. RBAC role enforcement
Needed for:
- emergency clinic admin access
- veterinarian review access
- operator visibility restrictions

2. Consent registry and purpose limitation
Needed for:
- emergency packet sharing
- owner-authorized disclosure
- access control to emergency summaries

### EP-02 Dependencies

3. Unified Pet Health Record
Needed for:
- allergies
- current medications
- history summary
- timeline retrieval for emergency packet

4. Document and media access controls
Needed for:
- emergency attachment inclusion
- packet visibility controls

### EP-03 Dependencies

5. Escalation engine semantics
Needed for:
- red-flag continuity
- emergency referral logic
- mandatory escalation handoff

6. Session and consultation linkage
Needed for:
- originating case context
- emergency packet provenance
- continuity of care traceability

7. Vet sign-off discipline
Needed for:
- trusted clinical summary inputs
- non-autonomous emergency packet content

### EP-04 Dependencies

8. Medication and safety lifecycle
Needed for:
- active medication list
- interaction relevance
- cold-chain or emergency medication context when applicable

9. Read-only and zero-side-effect service discipline
Needed for:
- deterministic emergency readiness planning
- safe routing explanation surfaces

### EP-05 Dependencies

10. Prompt/output logging foundation
Needed for:
- auditability if AI-assisted routing explanation is used later

11. HITL enforcement
Needed for:
- preserving assistive-only AI boundary in emergency flows

12. Evaluation and drift monitoring
Needed for:
- future governance on emergency AI assist surfaces

13. Runtime AI activation discipline
Needed for:
- future assistive emergency intake only
- not for autonomous routing

14. Approval resolution and sign-off binding
Needed for:
- ensuring clinically trusted summaries feed emergency packet generation

15. Dashboard and evidence/reporting chain
Needed for:
- emergency governance visibility
- hard-gate evidence completeness

## New EP-06 Native Capabilities Required

EP-06 must introduce the following new bounded capabilities:

- emergency clinic availability registry
- partner open/closed and capacity state
- ETA and failover candidate ranking
- explainable emergency routing decision output
- pre-arrival packet assembly contract
- emergency handoff trace model
- SLA-aware routing result surface

## Dependency Risk Notes

High-risk dependencies:
- consent semantics for emergency disclosure
- escalation continuity from EP-03
- clinically trusted packet inputs
- no AI autonomy leakage into routing decisions

## Planning Conclusion

EP-06 can begin without reopening any closed epic.
All dependencies are satisfied by governed prior state.
