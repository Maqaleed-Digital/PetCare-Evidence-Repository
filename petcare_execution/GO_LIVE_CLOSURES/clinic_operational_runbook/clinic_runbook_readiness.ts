export const CLINIC_RUNBOOK_READINESS = {
  clinicRunbookStatus: "COMPLETE",
  runbookSections: [
    "consultation_day_workflow",
    "pharmacy_handoff_workflow",
    "emergency_escalation_workflow",
    "clinic_shift_open_close_checklist",
  ],
  assistiveOnlyBoundaryPreserved: true,
  humanApprovalStillRequired: true,
} as const
