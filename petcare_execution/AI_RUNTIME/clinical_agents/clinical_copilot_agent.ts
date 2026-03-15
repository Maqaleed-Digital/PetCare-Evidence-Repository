export function clinicalCopilot(caseData) {

  return {
    summary: "Case summary generated",
    allergiesDetected: caseData.allergies || [],
    medicationFlags: [],
    assistiveOnly: true
  };

}
