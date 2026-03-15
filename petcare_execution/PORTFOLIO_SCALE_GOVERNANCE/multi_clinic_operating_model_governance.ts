export const MULTI_CLINIC_OPERATING_MODEL_GOVERNANCE = {
  multiClinicOperatingModelGovernanceStatus: "pass",
  checks: [
    "multi_clinic_role_model_defined",
    "clinic_governance_inheritance_defined",
    "shared_services_operating_model_defined",
    "clinic_activation_governance_path_defined",
    "cross_clinic_escalation_model_defined",
  ],
} as const
