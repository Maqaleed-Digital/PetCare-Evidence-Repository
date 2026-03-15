export const CLINICAL_OPERATIONS_RECONFIRMATION = {
  clinicalOperationsReconfirmed: true,
  checks: [
    "clinic_operational_runbook_complete",
    "consultation_workflow_confirmed",
    "pharmacy_handoff_confirmed",
    "emergency_escalation_confirmed",
    "shift_open_close_controls_confirmed",
  ],
  clinicalOperationsStatus: "pass",
} as const
