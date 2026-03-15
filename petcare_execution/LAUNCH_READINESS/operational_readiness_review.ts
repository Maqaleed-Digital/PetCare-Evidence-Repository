export const OPERATIONAL_READINESS_REVIEW = {
  status: "conditional",
  checks: [
    "clinic_activation_path_defined",
    "pilot_clinic_baseline_exists",
    "staffing_workflow_requires_final_go_live_confirmation",
    "pharmacy_operational_shift_closure_pending",
    "clinic_runbook_completion_pending",
  ],
  unresolvedOperationalDependencyCount: 2,
  launchLimitations: [
    "pharmacy_operator_go_live_confirmation_pending",
    "clinic_operational_runbook_completion_pending",
  ],
} as const
