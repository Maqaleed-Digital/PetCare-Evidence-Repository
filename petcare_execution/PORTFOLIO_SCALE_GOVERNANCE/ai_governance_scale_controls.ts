export const AI_GOVERNANCE_SCALE_CONTROLS = {
  aiGovernanceScaleControlsStatus: "pass",
  checks: [
    "cross_clinic_ai_policy_inheritance_defined",
    "override_reporting_rollup_defined",
    "assistive_only_boundary_scaling_preserved",
    "human_approval_scaling_controls_defined",
    "kill_switch_and_rollback_scale_controls_defined",
  ],
  aiScaleGovernanceState: "governed_multi_clinic_ai_controls_active",
} as const
