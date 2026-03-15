export interface DriftSignal {
  agent: string;
  driftDetected: boolean;
  driftScore: number;
  assistiveOnly: true;
}

export function detectOperationalDrift(
  baselineOverrideRate: number,
  currentOverrideRate: number,
  agent: string
): DriftSignal {

  const driftScore = Math.abs(currentOverrideRate - baselineOverrideRate)

  return {
    agent,
    driftDetected: driftScore > 0.15,
    driftScore,
    assistiveOnly: true
  }
}
