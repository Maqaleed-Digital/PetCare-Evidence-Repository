export const LIVE_OPERATIONS_REGISTRY = {
  liveOperationsRegistryStatus: "ACTIVE",
  clinicId: "pilot_clinic_001",
  runtimeState: "launch_active_under_governed_controls",
  operatingDomains: [
    "clinical_services",
    "pharmacy_operations",
    "billing_operations",
    "partner_network_operations",
    "ai_governance_monitoring",
    "incident_and_handover_management",
  ],
} as const
