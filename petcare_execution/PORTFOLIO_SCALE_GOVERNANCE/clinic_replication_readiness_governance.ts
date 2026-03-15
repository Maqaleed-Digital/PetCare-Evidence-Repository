export const CLINIC_REPLICATION_READINESS_GOVERNANCE = {
  clinicReplicationReadinessGovernanceStatus: "pass",
  checks: [
    "replication_readiness_gate_defined",
    "clinic_launch_template_defined",
    "core_controls_replication_path_defined",
    "staffing_and_enablement_replication_path_defined",
    "evidence_pack_replication_path_defined",
  ],
} as const
