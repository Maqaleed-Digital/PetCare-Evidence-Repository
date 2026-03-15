import { RouteDecision, TaskType } from "./types";

const ROUTE_MAP: Record<TaskType, RouteDecision> = {
  summarize_history: {
    agent: "clinical_copilot",
    rationale: "Clinical history summarization belongs to the clinical copilot.",
  },
  draft_consult_note: {
    agent: "clinical_copilot",
    rationale: "Consult note drafting belongs to the clinical copilot.",
  },
  medication_safety_review: {
    agent: "pharmacy_safety",
    rationale: "Medication interaction and contraindication review belongs to pharmacy safety.",
  },
  emergency_intake_support: {
    agent: "emergency_triage",
    rationale: "Emergency intake support belongs to emergency triage.",
  },
  operations_forecast: {
    agent: "operations_intelligence",
    rationale: "Demand and scheduling optimization belongs to operations intelligence.",
  },
  client_followup_draft: {
    agent: "client_communication",
    rationale: "Client reminders and follow-up drafting belong to client communication.",
  },
};

export class AgentRouter {
  route(taskType: TaskType): RouteDecision {
    return ROUTE_MAP[taskType];
  }
}
