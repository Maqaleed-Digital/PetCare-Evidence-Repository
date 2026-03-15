export const PHARMACY_OPERATIONS_MONITORING = {
  pharmacyOperationsMonitoringStatus: "pass",
  checks: [
    "pharmacy_operator_active",
    "dispense_controls_preserved",
    "pharmacy_handoff_path_active",
    "medication_audit_capture_active",
    "pharmacy_shift_monitoring_active",
  ],
} as const
