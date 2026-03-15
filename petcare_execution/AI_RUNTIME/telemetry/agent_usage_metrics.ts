export function agentUsageMetrics(agentName) {

  return {
    agent: agentName,
    usageCount: 0,
    overrideCount: 0,
    safetyFlags: 0
  };

}
