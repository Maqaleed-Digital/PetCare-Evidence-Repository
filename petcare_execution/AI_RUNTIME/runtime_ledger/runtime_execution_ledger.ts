export type LedgerRunStatus =
  | "accepted"
  | "blocked"
  | "review_required";

export interface RuntimeExecutionLedgerEntry {
  ledgerEntryId: string;
  requestId: string;
  taskFamily: string;
  agent: string;
  policyBundleId: string;
  promptBindingId: string;
  requiredReviewer: "veterinarian" | "pharmacist" | "admin" | "none";
  status: LedgerRunStatus;
  assistiveOnly: true;
  loggingConfirmed: true;
  safetyEventCodes: string[];
}

export const RUNTIME_EXECUTION_LEDGER_SAMPLE: RuntimeExecutionLedgerEntry[] = [
  {
    ledgerEntryId: "ledger_req_history_001",
    requestId: "req_history_001",
    taskFamily: "summarize_history",
    agent: "clinical_copilot",
    policyBundleId: "policy_summarize_history_v1",
    promptBindingId: "binding_summarize_history_v1",
    requiredReviewer: "veterinarian",
    status: "review_required",
    assistiveOnly: true,
    loggingConfirmed: true,
    safetyEventCodes: ["REVIEW_REQUIRED"],
  },
  {
    ledgerEntryId: "ledger_req_med_001",
    requestId: "req_med_001",
    taskFamily: "medication_safety_review",
    agent: "pharmacy_safety",
    policyBundleId: "policy_medication_safety_review_v1",
    promptBindingId: "binding_medication_safety_review_v1",
    requiredReviewer: "pharmacist",
    status: "review_required",
    assistiveOnly: true,
    loggingConfirmed: true,
    safetyEventCodes: ["REVIEW_REQUIRED"],
  },
  {
    ledgerEntryId: "ledger_req_followup_001",
    requestId: "req_followup_001",
    taskFamily: "client_followup_draft",
    agent: "client_communication",
    policyBundleId: "policy_client_followup_draft_v1",
    promptBindingId: "binding_client_followup_draft_v1",
    requiredReviewer: "none",
    status: "accepted",
    assistiveOnly: true,
    loggingConfirmed: true,
    safetyEventCodes: [],
  },
];

export class RuntimeExecutionLedger {
  list(): RuntimeExecutionLedgerEntry[] {
    return RUNTIME_EXECUTION_LEDGER_SAMPLE;
  }

  findByRequestId(requestId: string): RuntimeExecutionLedgerEntry | undefined {
    return RUNTIME_EXECUTION_LEDGER_SAMPLE.find((entry) => entry.requestId === requestId);
  }
}
