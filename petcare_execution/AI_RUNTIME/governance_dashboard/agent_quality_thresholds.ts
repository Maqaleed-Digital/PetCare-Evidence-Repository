export interface AgentQualityThreshold {
  agent: string;
  maxOverrideRate: number;
  maxSafetyFlags: number;
  minPositiveFeedbackRate: number;
}

export const AGENT_QUALITY_THRESHOLDS: AgentQualityThreshold[] = [
  {
    agent: "clinical_workflow_copilot",
    maxOverrideRate: 0.25,
    maxSafetyFlags: 0,
    minPositiveFeedbackRate: 0.70,
  },
  {
    agent: "triage_assistant",
    maxOverrideRate: 0.20,
    maxSafetyFlags: 0,
    minPositiveFeedbackRate: 0.75,
  },
  {
    agent: "documentation_assistant",
    maxOverrideRate: 0.30,
    maxSafetyFlags: 0,
    minPositiveFeedbackRate: 0.65,
  }
];
