export interface EmergencyWorkflowInput {
  incidentId: string;
  queueIds: string[];
  emergencySignals: string[];
}

export interface EmergencyWorkflowOutput {
  workflow: "emergency";
  agent: "emergency_coordination_agent";
  assistiveOnly: true;
  humanApprovalRequired: true;
  payload: {
    incidentId: string;
    prioritizedQueueIds: string[];
    escalationHint: boolean;
  };
}

export function buildEmergencyWorkflowIntegration(
  input: EmergencyWorkflowInput,
): EmergencyWorkflowOutput {
  return {
    workflow: "emergency",
    agent: "emergency_coordination_agent",
    assistiveOnly: true,
    humanApprovalRequired: true,
    payload: {
      incidentId: input.incidentId,
      prioritizedQueueIds: input.queueIds,
      escalationHint: input.emergencySignals.length > 0,
    },
  };
}
