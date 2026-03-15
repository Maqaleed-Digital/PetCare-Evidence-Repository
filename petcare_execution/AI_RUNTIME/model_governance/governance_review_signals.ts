export interface GovernanceReviewSignalInput {
  agent: string;
  overrideCount: number;
  safetyFlags: number;
  feedbackRating: "useful" | "needs_review" | "not_useful";
}

export interface GovernanceReviewSignal {
  agent: string;
  reviewRequired: boolean;
  reasonCodes: string[];
  assistiveOnly: true;
}

export function buildGovernanceReviewSignal(
  input: GovernanceReviewSignalInput,
): GovernanceReviewSignal {
  const reasonCodes: string[] = [];

  if (input.overrideCount > 0) {
    reasonCodes.push("override_detected");
  }
  if (input.safetyFlags > 0) {
    reasonCodes.push("safety_flag_detected");
  }
  if (input.feedbackRating !== "useful") {
    reasonCodes.push("feedback_review_required");
  }

  return {
    agent: input.agent,
    reviewRequired: reasonCodes.length > 0,
    reasonCodes,
    assistiveOnly: true,
  };
}
