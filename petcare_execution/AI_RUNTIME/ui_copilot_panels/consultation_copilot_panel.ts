export function consultationCopilotPanel(data) {

  return {
    panel: "consultation_copilot",
    assistiveOnly: true,
    insights: {
      summaryHint: true,
      allergyHighlight: data.allergies || [],
      medicationFlags: []
    },
    requiresHumanApproval: true
  };

}
