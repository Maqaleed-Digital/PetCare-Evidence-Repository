export function triageAIPanel(caseData) {

  return {
    panel: "triage_ai_panel",
    assistiveOnly: true,
    signalsDetected: caseData.symptoms,
    suggestedTriageState: "review_required",
    requiresHumanApproval: true
  };

}
