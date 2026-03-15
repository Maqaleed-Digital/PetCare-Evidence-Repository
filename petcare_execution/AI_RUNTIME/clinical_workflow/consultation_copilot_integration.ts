export interface ConsultationWorkflowInput {
  consultationId: string;
  petId: string;
  symptoms: string[];
  allergies: string[];
  medications: string[];
}

export interface ConsultationWorkflowOutput {
  workflow: "consultation";
  agent: "clinical_copilot_agent";
  assistiveOnly: true;
  humanApprovalRequired: true;
  payload: {
    summaryRequest: string;
    allergiesHighlighted: string[];
    medicationReviewRequested: boolean;
  };
}

export function buildConsultationCopilotIntegration(
  input: ConsultationWorkflowInput,
): ConsultationWorkflowOutput {
  return {
    workflow: "consultation",
    agent: "clinical_copilot_agent",
    assistiveOnly: true,
    humanApprovalRequired: true,
    payload: {
      summaryRequest: `Summarize consultation ${input.consultationId} for pet ${input.petId}`,
      allergiesHighlighted: input.allergies,
      medicationReviewRequested: input.medications.length > 0,
    },
  };
}
