export interface EscalationSignal {
  agent: string
  escalationRequired: boolean
  freezeRecommended: boolean
  reasonCodes: string[]
  assistiveOnly: true
}

export function buildEscalationSignal(
  driftDetected: boolean,
  safetyBreach: boolean,
  agent: string
): EscalationSignal {

  const reasons: string[] = []

  if (driftDetected)
    reasons.push("operational_drift_detected")

  if (safetyBreach)
    reasons.push("safety_guardrail_breach")

  return {
    agent,
    escalationRequired: reasons.length > 0,
    freezeRecommended: safetyBreach,
    reasonCodes: reasons,
    assistiveOnly: true
  }
}
