export const LAUNCH_ACTIVATION_REGISTRY = {
  launchActivationRegistryStatus: "ACTIVE",
  clinicId: "pilot_clinic_001",
  activationScope: [
    "consultation",
    "triage",
    "pharmacy_review",
    "emergency",
    "billing",
    "partner_network",
  ],
  activationAuthority: "PETCARE_GOVERNED_LAUNCH_AUTHORITY",
} as const
