export interface AuditChainAnchor {
  anchorId: string;
  requestId: string;
  policyBundleId: string;
  promptBindingId: string;
  safetyEventCodes: string[];
  outputSummaryDigestHint: string;
  validationState: "validated";
}

export const AUDIT_CHAIN_ANCHORS: AuditChainAnchor[] = [
  {
    anchorId: "anchor_req_history_001",
    requestId: "req_history_001",
    policyBundleId: "policy_summarize_history_v1",
    promptBindingId: "binding_summarize_history_v1",
    safetyEventCodes: ["REVIEW_REQUIRED"],
    outputSummaryDigestHint: "digest_hint_req_history_001",
    validationState: "validated",
  },
  {
    anchorId: "anchor_req_med_001",
    requestId: "req_med_001",
    policyBundleId: "policy_medication_safety_review_v1",
    promptBindingId: "binding_medication_safety_review_v1",
    safetyEventCodes: ["REVIEW_REQUIRED"],
    outputSummaryDigestHint: "digest_hint_req_med_001",
    validationState: "validated",
  },
  {
    anchorId: "anchor_req_followup_001",
    requestId: "req_followup_001",
    policyBundleId: "policy_client_followup_draft_v1",
    promptBindingId: "binding_client_followup_draft_v1",
    safetyEventCodes: [],
    outputSummaryDigestHint: "digest_hint_req_followup_001",
    validationState: "validated",
  },
];

export class AuditChainAnchors {
  list(): AuditChainAnchor[] {
    return AUDIT_CHAIN_ANCHORS;
  }

  findByRequestId(requestId: string): AuditChainAnchor | undefined {
    return AUDIT_CHAIN_ANCHORS.find((anchor) => anchor.requestId === requestId);
  }
}
