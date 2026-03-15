export interface HumanApprovalEnforcement {
  workflow: string
  approvalRequired: boolean
  clinicalAuthorityPreserved: true
  assistiveOnlyBoundaryPreserved: true
}

export const HUMAN_APPROVAL_ENFORCEMENT: HumanApprovalEnforcement[] = [
  {
    workflow: "consultation",
    approvalRequired: true,
    clinicalAuthorityPreserved: true,
    assistiveOnlyBoundaryPreserved: true
  },
  {
    workflow: "triage",
    approvalRequired: true,
    clinicalAuthorityPreserved: true,
    assistiveOnlyBoundaryPreserved: true
  },
  {
    workflow: "pharmacy_review",
    approvalRequired: true,
    clinicalAuthorityPreserved: true,
    assistiveOnlyBoundaryPreserved: true
  },
  {
    workflow: "emergency",
    approvalRequired: true,
    clinicalAuthorityPreserved: true,
    assistiveOnlyBoundaryPreserved: true
  }
]
