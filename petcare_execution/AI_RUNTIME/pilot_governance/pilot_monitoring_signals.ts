export interface PilotMonitoringSignal {
  agent: string
  overrideRate: number
  safetyFlags: number
  driftDetected: boolean
  assistiveOnly: true
}

export function buildPilotMonitoringSignal(
  agent: string,
  overrideRate: number,
  safetyFlags: number,
  driftDetected: boolean
): PilotMonitoringSignal {

  return {
    agent,
    overrideRate,
    safetyFlags,
    driftDetected,
    assistiveOnly: true
  }
}
