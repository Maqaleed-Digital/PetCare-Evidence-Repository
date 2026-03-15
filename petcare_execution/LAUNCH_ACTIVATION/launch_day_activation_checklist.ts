export const LAUNCH_DAY_ACTIVATION_CHECKLIST = {
  launchDayChecklistStatus: "pass",
  checks: [
    "staff_presence_confirmed",
    "clinic_access_ready",
    "consultation_queue_ready",
    "pharmacy_operator_ready",
    "billing_access_ready",
    "partner_routing_ready",
    "emergency_path_ready",
    "audit_capture_confirmed",
  ],
} as const
