export interface GovernanceDashboardMetrics {
  agent: string;
  usageCount: number;
  overrideRate: number;
  safetyFlags: number;
  positiveFeedbackRate: number;
  assistiveOnly: true;
}

export function buildGovernanceMetrics(
  agent: string,
  usageCount: number,
  overrides: number,
  safetyFlags: number,
  positiveFeedbackRate: number
): GovernanceDashboardMetrics {

  const overrideRate =
    usageCount === 0 ? 0 : overrides / usageCount;

  return {
    agent,
    usageCount,
    overrideRate,
    safetyFlags,
    positiveFeedbackRate,
    assistiveOnly: true
  };
}
