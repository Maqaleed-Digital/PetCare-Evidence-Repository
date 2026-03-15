export const SAFETY_REVIEW_CHECKPOINT = {
  pilotClinicId: "pilot_clinic_001",
  cohortId: "AI_PILOT_ALPHA",
  safetyChecks: [
    "assistive_only_boundary",
    "human_approval_enforcement",
    "kill_switch_available",
    "rollback_available",
    "regulated_action_blocking",
    "escalation_path_integrity",
  ],
  safetyCheckpointStatus: "pass",
  assistiveOnlyBoundaryPreserved: true,
  humanApprovalStillRequired: true,
  safetyIncidentCount: 0,
} as const
