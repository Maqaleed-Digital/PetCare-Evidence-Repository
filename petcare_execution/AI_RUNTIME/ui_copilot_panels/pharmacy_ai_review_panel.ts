export function pharmacyAIReviewPanel(prescription) {

  return {
    panel: "pharmacy_ai_review",
    assistiveOnly: true,
    interactionWarnings: [],
    dosageAlerts: [],
    requiresHumanApproval: true
  };

}
