export interface DeploymentPromotionSignal {
  agent: string;
  promotionEligible: boolean;
  reasonCodes: string[];
  assistiveOnly: true;
}

export function evaluatePromotionSignal(
  overrideRate: number,
  safetyFlags: number,
  positiveFeedbackRate: number,
  thresholds: {
    maxOverrideRate: number
    maxSafetyFlags: number
    minPositiveFeedbackRate: number
  },
  agent: string
): DeploymentPromotionSignal {

  const reasons: string[] = [];

  if (overrideRate > thresholds.maxOverrideRate)
    reasons.push("override_rate_exceeded");

  if (safetyFlags > thresholds.maxSafetyFlags)
    reasons.push("safety_flags_detected");

  if (positiveFeedbackRate < thresholds.minPositiveFeedbackRate)
    reasons.push("feedback_below_threshold");

  return {
    agent,
    promotionEligible: reasons.length === 0,
    reasonCodes: reasons,
    assistiveOnly: true
  };
}
