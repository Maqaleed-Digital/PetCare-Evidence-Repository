export interface SafetyGuardrailEvent {
  agent: string
  safetyFlags: number
  breachDetected: boolean
  breachType: "none" | "safety_flags_detected"
  assistiveOnly: true
}

export function classifySafetyGuardrail(
  agent: string,
  safetyFlags: number
): SafetyGuardrailEvent {

  const breach = safetyFlags > 0

  return {
    agent,
    safetyFlags,
    breachDetected: breach,
    breachType: breach ? "safety_flags_detected" : "none",
    assistiveOnly: true
  }
}
