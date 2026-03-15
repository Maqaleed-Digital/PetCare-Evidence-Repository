export function emergencyCoordinationAgent(queueData) {

  return {
    prioritizedQueue: queueData,
    emergencySignals: [],
    assistiveOnly: true
  };

}
