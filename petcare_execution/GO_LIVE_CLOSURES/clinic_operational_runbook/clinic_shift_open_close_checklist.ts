export const CLINIC_SHIFT_OPEN_CLOSE_CHECKLIST = {
  checklistName: "clinic_shift_open_close_checklist",
  openingChecks: [
    "staff_presence_confirmed",
    "system_access_confirmed",
    "consultation_queue_ready",
    "pharmacy_readiness_confirmed",
    "emergency_contact_path_available",
  ],
  closingChecks: [
    "open_consultations_resolved_or_handed_over",
    "dispense_log_reconciled",
    "incident_flags_reviewed",
    "audit_log_capture_confirmed",
    "next_shift_handover_recorded",
  ],
  shiftChecklistStatus: "pass",
} as const
