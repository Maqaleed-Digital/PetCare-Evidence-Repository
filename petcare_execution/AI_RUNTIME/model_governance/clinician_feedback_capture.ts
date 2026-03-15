export interface ClinicianFeedbackInput {
  requestId: string;
  agent: string;
  workflow: string;
  rating: "useful" | "needs_review" | "not_useful";
  note?: string;
}

export interface ClinicianFeedbackRecord {
  requestId: string;
  agent: string;
  workflow: string;
  rating: "useful" | "needs_review" | "not_useful";
  note: string;
  assistiveOnly: true;
  governanceRelevant: true;
}

export function captureClinicianFeedback(
  input: ClinicianFeedbackInput,
): ClinicianFeedbackRecord {
  return {
    requestId: input.requestId,
    agent: input.agent,
    workflow: input.workflow,
    rating: input.rating,
    note: input.note ?? "",
    assistiveOnly: true,
    governanceRelevant: true,
  };
}
