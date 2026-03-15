export interface DeploymentApprovalGate {
  gateName: string
  required: boolean
  passed: boolean
  assistiveOnly: true
}

export const DEPLOYMENT_APPROVAL_GATES: DeploymentApprovalGate[] = [
  {
    gateName: "clinical_safety_review",
    required: true,
    passed: true,
    assistiveOnly: true
  },
  {
    gateName: "pilot_monitoring_pass",
    required: true,
    passed: true,
    assistiveOnly: true
  }
]
