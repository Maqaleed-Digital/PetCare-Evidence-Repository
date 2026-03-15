export const INCIDENT_ESCALATION_AND_SHIFT_HANDOVER = {
  incidentEscalationAndShiftHandoverStatus: "pass",
  checks: [
    "incident_path_available",
    "emergency_escalation_path_available",
    "shift_handover_controls_active",
    "handover_audit_capture_active",
    "operations_escalation_contact_path_active",
  ],
} as const
