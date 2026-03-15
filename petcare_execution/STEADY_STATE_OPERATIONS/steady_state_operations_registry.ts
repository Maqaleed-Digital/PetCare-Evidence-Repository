export const STEADY_STATE_OPERATIONS_REGISTRY = {
  steadyStateOperationsRegistryStatus: "ACTIVE",
  clinicId: "pilot_clinic_001",
  runtimeState: "governed_assistive_operations_active",
  managementDomains: [
    "service_quality_and_sla_monitoring",
    "clinical_safety_and_audit_monitoring",
    "pharmacy_billing_partner_performance_monitoring",
    "ai_governance_and_override_monitoring",
    "incident_review_and_continuity_management",
  ],
} as const
