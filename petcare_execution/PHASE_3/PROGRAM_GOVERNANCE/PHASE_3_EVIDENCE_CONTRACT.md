PHASE 3 EVIDENCE CONTRACT

PURPOSE

Define the evidence obligations for the whole of Phase 3.

REQUIRED EVIDENCE FOR EVERY PHASE 3 WORKSTREAM

- decision_log.txt
- active.log
- file_list.txt
- summary.txt
- MANIFEST.json

OPTIONAL BUT EXPECTED WHEN APPLICABLE

- blocked.log
- rollback_check.txt
- gate_matrix.txt
- approval_posture.txt
- integrity_check.txt

MANDATORY EVIDENCE RULES

1. every workstream must generate an evidence directory
2. every evidence directory must be timestamped in UTC
3. every phase artifact must be included in MANIFEST.json with SHA256
4. every blocked outcome must still produce evidence
5. every activation-related decision must identify approval posture
6. every live-exposure step must identify rollback readiness
7. no evidence pack may imply granted access without explicit stage context

PHASE 3 INTEGRITY RULES

- evidence must remain reproducible
- evidence must remain commit-anchored
- evidence must remain stage-specific
- evidence must remain audit-ready
- evidence must remain fail-closed

FAIL-CLOSED CONDITIONS

If MANIFEST.json is missing:
- block stage completion

If SHA256 coverage is incomplete:
- block stage completion

If decision log is missing:
- block stage completion

If rollback readiness is required but not evidenced:
- block stage completion

OUTCOME

Phase 3 evidence remains trust-grade across sandbox, limited production, monitoring, certification, and scale-out.
