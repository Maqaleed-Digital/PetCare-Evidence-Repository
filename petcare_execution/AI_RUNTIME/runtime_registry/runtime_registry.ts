export type RegisteredAgentKind =
  | "clinical_copilot"
  | "pharmacy_safety"
  | "emergency_triage"
  | "operations_intelligence"
  | "client_communication";

export type RegisteredTaskFamily =
  | "summarize_history"
  | "draft_consult_note"
  | "medication_safety_review"
  | "emergency_intake_support"
  | "operations_forecast"
  | "client_followup_draft";

export type RequiredReviewer =
  | "veterinarian"
  | "pharmacist"
  | "admin"
  | "none";

export interface RuntimeRegistryEntry {
  agent: RegisteredAgentKind;
  taskFamily: RegisteredTaskFamily;
  assistiveOnly: true;
  allowedCapabilities: string[];
  prohibitedCapabilities: string[];
  requiredReviewer: RequiredReviewer;
}

export const RUNTIME_REGISTRY: RuntimeRegistryEntry[] = [
  {
    agent: "clinical_copilot",
    taskFamily: "summarize_history",
    assistiveOnly: true,
    allowedCapabilities: [
      "history summarization",
      "context highlighting",
      "non-final draft support",
    ],
    prohibitedCapabilities: [
      "autonomous diagnosis",
      "autonomous treatment authorization",
      "medical record signing",
    ],
    requiredReviewer: "veterinarian",
  },
  {
    agent: "clinical_copilot",
    taskFamily: "draft_consult_note",
    assistiveOnly: true,
    allowedCapabilities: [
      "draft consultation note",
      "structured note preparation",
      "clinical draft support",
    ],
    prohibitedCapabilities: [
      "consultation closure",
      "medical record signing",
      "autonomous diagnosis",
    ],
    requiredReviewer: "veterinarian",
  },
  {
    agent: "pharmacy_safety",
    taskFamily: "medication_safety_review",
    assistiveOnly: true,
    allowedCapabilities: [
      "interaction review",
      "contraindication review",
      "dose anomaly flagging",
    ],
    prohibitedCapabilities: [
      "autonomous prescription",
      "dispense authorization override",
      "treatment authorization",
    ],
    requiredReviewer: "pharmacist",
  },
  {
    agent: "emergency_triage",
    taskFamily: "emergency_intake_support",
    assistiveOnly: true,
    allowedCapabilities: [
      "red flag organization",
      "urgent symptom structuring",
      "stabilization checklist drafting",
    ],
    prohibitedCapabilities: [
      "final triage decision",
      "autonomous emergency disposition",
      "treatment authorization",
    ],
    requiredReviewer: "veterinarian",
  },
  {
    agent: "operations_intelligence",
    taskFamily: "operations_forecast",
    assistiveOnly: true,
    allowedCapabilities: [
      "demand forecasting",
      "inventory signal highlighting",
      "schedule optimization support",
    ],
    prohibitedCapabilities: [
      "clinical decision making",
      "medication authorization",
      "treatment authorization",
    ],
    requiredReviewer: "admin",
  },
  {
    agent: "client_communication",
    taskFamily: "client_followup_draft",
    assistiveOnly: true,
    allowedCapabilities: [
      "reminder drafting",
      "follow-up communication drafting",
      "non-diagnostic engagement support",
    ],
    prohibitedCapabilities: [
      "clinical advice finalization",
      "diagnosis communication as authority",
      "prescription issuance",
    ],
    requiredReviewer: "none",
  },
];

export class RuntimeRegistry {
  list(): RuntimeRegistryEntry[] {
    return RUNTIME_REGISTRY;
  }

  findByTask(taskFamily: RegisteredTaskFamily): RuntimeRegistryEntry | undefined {
    return RUNTIME_REGISTRY.find((entry) => entry.taskFamily === taskFamily);
  }
}
