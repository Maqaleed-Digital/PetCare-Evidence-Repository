export interface FreezeRollbackSignal {
  agent: string
  freezeRecommended: boolean
  rollbackRecommended: boolean
  reasonCodes: string[]
  assistiveOnly: true
}

export function evaluateFreezeRollback(
  safetyFlags: number,
  driftDetected: boolean,
  agent: string
): FreezeRollbackSignal {

  const reasons: string[] = []

  if (safetyFlags > 0)
    reasons.push("safety_breach")

  if (driftDetected)
    reasons.push("behavioral_drift")

  return {
    agent,
    freezeRecommended: reasons.length > 0,
    rollbackRecommended: safetyFlags > 0,
    reasonCodes: reasons,
    assistiveOnly: true
  }
}
