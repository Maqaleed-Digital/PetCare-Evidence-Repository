export function triageSupportAgent(symptoms) {

  return {
    suggestedTriageLevel: "review_required",
    signalsDetected: symptoms,
    assistiveOnly: true
  };

}
