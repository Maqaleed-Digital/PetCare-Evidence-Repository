export interface PromptRefinementInput {
  promptTemplateId: string;
  feedbackTrend: "stable" | "review_required";
  governanceReasons: string[];
}

export interface PromptRefinementOutput {
  promptTemplateId: string;
  refinementAction: "retain" | "review";
  governanceReasons: string[];
  assistiveOnly: true;
}

export function buildPromptRefinementPlan(
  input: PromptRefinementInput,
): PromptRefinementOutput {
  return {
    promptTemplateId: input.promptTemplateId,
    refinementAction:
      input.feedbackTrend === "review_required" ? "review" : "retain",
    governanceReasons: input.governanceReasons,
    assistiveOnly: true,
  };
}
