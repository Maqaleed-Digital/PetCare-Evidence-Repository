export function emergencyCoordinationPanel(queue) {

  return {
    panel: "emergency_coordination_panel",
    assistiveOnly: true,
    queueInsights: queue,
    escalationHints: [],
    requiresHumanApproval: true
  };

}
