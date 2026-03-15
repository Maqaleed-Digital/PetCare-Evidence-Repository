export type SafetyEventCode =
  | "AUTONOMOUS_DIAGNOSIS_BLOCKED"
  | "AUTONOMOUS_PRESCRIPTION_BLOCKED"
  | "AUTONOMOUS_TREATMENT_AUTHORIZATION_BLOCKED"
  | "CONSULTATION_CLOSURE_BLOCKED"
  | "FINAL_TRIAGE_DECISION_BLOCKED"
  | "OVERRIDE_REQUEST_RECORDED"
  | "REVIEW_REQUIRED"
  | "ESCALATION_REQUIRED"
  | "REGISTRY_POLICY_MISMATCH";

export interface SafetyEventDefinition {
  code: SafetyEventCode;
  severity: "high" | "medium" | "info";
  category:
    | "blocked_autonomous_action"
    | "override"
    | "review"
    | "escalation"
    | "policy_integrity";
  description: string;
}

export const SAFETY_EVENT_TAXONOMY: SafetyEventDefinition[] = [
  {
    code: "AUTONOMOUS_DIAGNOSIS_BLOCKED",
    severity: "high",
    category: "blocked_autonomous_action",
    description: "Attempted autonomous diagnosis was blocked by policy.",
  },
  {
    code: "AUTONOMOUS_PRESCRIPTION_BLOCKED",
    severity: "high",
    category: "blocked_autonomous_action",
    description: "Attempted autonomous prescription action was blocked by policy.",
  },
  {
    code: "AUTONOMOUS_TREATMENT_AUTHORIZATION_BLOCKED",
    severity: "high",
    category: "blocked_autonomous_action",
    description: "Attempted treatment authorization without human approval was blocked.",
  },
  {
    code: "CONSULTATION_CLOSURE_BLOCKED",
    severity: "high",
    category: "blocked_autonomous_action",
    description: "Attempted autonomous consultation closure was blocked.",
  },
  {
    code: "FINAL_TRIAGE_DECISION_BLOCKED",
    severity: "high",
    category: "blocked_autonomous_action",
    description: "Attempted final triage decision without clinician review was blocked.",
  },
  {
    code: "OVERRIDE_REQUEST_RECORDED",
    severity: "medium",
    category: "override",
    description: "A governed override request was recorded.",
  },
  {
    code: "REVIEW_REQUIRED",
    severity: "medium",
    category: "review",
    description: "Human reviewer is required before governed use proceeds.",
  },
  {
    code: "ESCALATION_REQUIRED",
    severity: "medium",
    category: "escalation",
    description: "Case requires escalation handling under safety rules.",
  },
  {
    code: "REGISTRY_POLICY_MISMATCH",
    severity: "high",
    category: "policy_integrity",
    description: "Runtime behavior and registry policy mapping are inconsistent.",
  },
];

export class SafetyEventTaxonomy {
  list(): SafetyEventDefinition[] {
    return SAFETY_EVENT_TAXONOMY;
  }

  findByCode(code: SafetyEventCode): SafetyEventDefinition | undefined {
    return SAFETY_EVENT_TAXONOMY.find((event) => event.code === code);
  }
}
