export interface ModelPerformanceInput {
  agent: string;
  usageCount: number;
  overrideCount: number;
  safetyFlags: number;
}

export interface ModelPerformanceScore {
  agent: string;
  governanceScoreBand: "stable" | "review_required";
  usageCount: number;
  overrideCount: number;
  safetyFlags: number;
  assistiveOnly: true;
}

export function scoreModelPerformance(
  input: ModelPerformanceInput,
): ModelPerformanceScore {
  const governanceScoreBand =
    input.overrideCount > 0 || input.safetyFlags > 0
      ? "review_required"
      : "stable";

  return {
    agent: input.agent,
    governanceScoreBand,
    usageCount: input.usageCount,
    overrideCount: input.overrideCount,
    safetyFlags: input.safetyFlags,
    assistiveOnly: true,
  };
}
