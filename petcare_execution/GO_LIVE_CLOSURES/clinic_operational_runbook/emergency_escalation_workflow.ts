export const EMERGENCY_ESCALATION_WORKFLOW = {
  workflowName: "emergency_escalation_workflow",
  steps: [
    "red_flag_identification",
    "mandatory_human_review",
    "emergency_partner_selection",
    "pre_arrival_packet_preparation",
    "handoff_confirmation",
  ],
  emergencyEscalationWorkflowStatus: "pass",
  escalationRemainsHumanDirected: true,
} as const
