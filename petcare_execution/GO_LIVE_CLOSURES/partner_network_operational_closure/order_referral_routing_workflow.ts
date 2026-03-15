export const ORDER_REFERRAL_ROUTING_WORKFLOW = {
  workflowName: "order_referral_routing_workflow",
  steps: [
    "eligible_partner_selection",
    "routing_decision_recorded",
    "partner_assignment_confirmed",
    "status_transition_audit_logged",
    "handoff_or_completion_confirmation_recorded",
  ],
  orderReferralRoutingStatus: "pass",
  regulatedActionHumanControlled: true,
} as const
