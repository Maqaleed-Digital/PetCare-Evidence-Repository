export const LAUNCH_GOVERNANCE_NOTIFICATION = {
  launchGovernanceNotificationStatus: "recorded",
  recipients: [
    "petcare_governed_launch_authority",
    "clinical_operations_owner",
    "pharmacy_operations_owner",
    "platform_operations_owner",
  ],
  notificationType: "clinic_launch_activation_record",
} as const
