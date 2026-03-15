export type PolicyBundleTaskFamily =
  | "summarize_history"
  | "draft_consult_note"
  | "medication_safety_review"
  | "emergency_intake_support"
  | "operations_forecast"
  | "client_followup_draft";

export type PolicyBundleReviewer =
  | "veterinarian"
  | "pharmacist"
  | "admin"
  | "none";

export interface RuntimePolicyBundle {
  bundleId: string;
  taskFamily: PolicyBundleTaskFamily;
  assistiveOnly: true;
  requiredReviewer: PolicyBundleReviewer;
  loggingRequired: true;
  overrideEligible: boolean;
  blockedActionClasses: string[];
}

export const RUNTIME_POLICY_BUNDLES: RuntimePolicyBundle[] = [
  {
    bundleId: "policy_summarize_history_v1",
    taskFamily: "summarize_history",
    assistiveOnly: true,
    requiredReviewer: "veterinarian",
    loggingRequired: true,
    overrideEligible: true,
    blockedActionClasses: [
      "autonomous diagnosis",
      "treatment authorization",
      "clinical sign-off",
    ],
  },
  {
    bundleId: "policy_draft_consult_note_v1",
    taskFamily: "draft_consult_note",
    assistiveOnly: true,
    requiredReviewer: "veterinarian",
    loggingRequired: true,
    overrideEligible: true,
    blockedActionClasses: [
      "consultation closure",
      "medical record signing",
      "autonomous diagnosis",
    ],
  },
  {
    bundleId: "policy_medication_safety_review_v1",
    taskFamily: "medication_safety_review",
    assistiveOnly: true,
    requiredReviewer: "pharmacist",
    loggingRequired: true,
    overrideEligible: true,
    blockedActionClasses: [
      "autonomous prescription",
      "dispense authorization override",
      "treatment authorization",
    ],
  },
  {
    bundleId: "policy_emergency_intake_support_v1",
    taskFamily: "emergency_intake_support",
    assistiveOnly: true,
    requiredReviewer: "veterinarian",
    loggingRequired: true,
    overrideEligible: true,
    blockedActionClasses: [
      "final triage decision",
      "autonomous emergency disposition",
      "treatment authorization",
    ],
  },
  {
    bundleId: "policy_operations_forecast_v1",
    taskFamily: "operations_forecast",
    assistiveOnly: true,
    requiredReviewer: "admin",
    loggingRequired: true,
    overrideEligible: false,
    blockedActionClasses: [
      "clinical decision making",
      "medication authorization",
      "treatment authorization",
    ],
  },
  {
    bundleId: "policy_client_followup_draft_v1",
    taskFamily: "client_followup_draft",
    assistiveOnly: true,
    requiredReviewer: "none",
    loggingRequired: true,
    overrideEligible: false,
    blockedActionClasses: [
      "clinical advice finalization",
      "diagnosis communication as authority",
      "prescription issuance",
    ],
  },
];

export class RuntimePolicyBundles {
  list(): RuntimePolicyBundle[] {
    return RUNTIME_POLICY_BUNDLES;
  }

  findByTask(taskFamily: PolicyBundleTaskFamily): RuntimePolicyBundle | undefined {
    return RUNTIME_POLICY_BUNDLES.find((bundle) => bundle.taskFamily === taskFamily);
  }
}
