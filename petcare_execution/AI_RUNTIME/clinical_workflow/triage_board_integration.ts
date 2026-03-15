export interface TriageBoardInput {
  caseId: string;
  symptoms: string[];
  emergencySignals: string[];
}

export interface TriageBoardOutput {
  workflow: "triage_board";
  agent: "triage_support_agent";
  assistiveOnly: true;
  humanApprovalRequired: true;
  payload: {
    suggestedTriageState: "review_required";
    detectedSignals: string[];
    escalationHint: boolean;
  };
}

export function buildTriageBoardIntegration(
  input: TriageBoardInput,
): TriageBoardOutput {
  return {
    workflow: "triage_board",
    agent: "triage_support_agent",
    assistiveOnly: true,
    humanApprovalRequired: true,
    payload: {
      suggestedTriageState: "review_required",
      detectedSignals: [...input.symptoms, ...input.emergencySignals],
      escalationHint: input.emergencySignals.length > 0,
    },
  };
}
