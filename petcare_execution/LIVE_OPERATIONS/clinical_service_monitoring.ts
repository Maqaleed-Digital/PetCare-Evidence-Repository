export const CLINICAL_SERVICE_MONITORING = {
  clinicalServiceMonitoringStatus: "pass",
  checks: [
    "consultation_flow_active",
    "human_signoff_preserved",
    "triage_escalation_path_active",
    "clinical_audit_capture_active",
    "shift_level_clinical_monitoring_active",
  ],
} as const
