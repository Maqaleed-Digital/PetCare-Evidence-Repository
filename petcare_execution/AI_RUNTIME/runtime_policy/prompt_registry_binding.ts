export type BindingAgentKind =
  | "clinical_copilot"
  | "pharmacy_safety"
  | "emergency_triage"
  | "operations_intelligence"
  | "client_communication";

export interface PromptRegistryBinding {
  bindingId: string;
  taskFamily: string;
  agent: BindingAgentKind;
  promptTemplateId: string;
  promptSchemaVersion: "v1";
  policyBundleId: string;
}

export const PROMPT_REGISTRY_BINDINGS: PromptRegistryBinding[] = [
  {
    bindingId: "binding_summarize_history_v1",
    taskFamily: "summarize_history",
    agent: "clinical_copilot",
    promptTemplateId: "prompt_tpl_summarize_history_v1",
    promptSchemaVersion: "v1",
    policyBundleId: "policy_summarize_history_v1",
  },
  {
    bindingId: "binding_draft_consult_note_v1",
    taskFamily: "draft_consult_note",
    agent: "clinical_copilot",
    promptTemplateId: "prompt_tpl_draft_consult_note_v1",
    promptSchemaVersion: "v1",
    policyBundleId: "policy_draft_consult_note_v1",
  },
  {
    bindingId: "binding_medication_safety_review_v1",
    taskFamily: "medication_safety_review",
    agent: "pharmacy_safety",
    promptTemplateId: "prompt_tpl_medication_safety_review_v1",
    promptSchemaVersion: "v1",
    policyBundleId: "policy_medication_safety_review_v1",
  },
  {
    bindingId: "binding_emergency_intake_support_v1",
    taskFamily: "emergency_intake_support",
    agent: "emergency_triage",
    promptTemplateId: "prompt_tpl_emergency_intake_support_v1",
    promptSchemaVersion: "v1",
    policyBundleId: "policy_emergency_intake_support_v1",
  },
  {
    bindingId: "binding_operations_forecast_v1",
    taskFamily: "operations_forecast",
    agent: "operations_intelligence",
    promptTemplateId: "prompt_tpl_operations_forecast_v1",
    promptSchemaVersion: "v1",
    policyBundleId: "policy_operations_forecast_v1",
  },
  {
    bindingId: "binding_client_followup_draft_v1",
    taskFamily: "client_followup_draft",
    agent: "client_communication",
    promptTemplateId: "prompt_tpl_client_followup_draft_v1",
    promptSchemaVersion: "v1",
    policyBundleId: "policy_client_followup_draft_v1",
  },
];

export class PromptRegistryBindingStore {
  list(): PromptRegistryBinding[] {
    return PROMPT_REGISTRY_BINDINGS;
  }

  findByTask(taskFamily: string): PromptRegistryBinding | undefined {
    return PROMPT_REGISTRY_BINDINGS.find((binding) => binding.taskFamily === taskFamily);
  }
}
