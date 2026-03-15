export type AgentKind =
  | "clinical_copilot"
  | "pharmacy_safety"
  | "emergency_triage"
  | "operations_intelligence"
  | "client_communication";

export type ActorRole =
  | "owner"
  | "veterinarian"
  | "pharmacy_operator"
  | "partner_admin"
  | "platform_admin";

export type TaskType =
  | "summarize_history"
  | "draft_consult_note"
  | "medication_safety_review"
  | "emergency_intake_support"
  | "operations_forecast"
  | "client_followup_draft";

export interface OrchestratorSubjectContext {
  tenantId: string;
  clinicId?: string;
  petId?: string;
  consultationId?: string;
  prescriptionId?: string;
  emergencyCaseId?: string;
}

export interface OrchestratorInputEnvelope {
  summary?: string;
  symptoms?: string[];
  allergies?: string[];
  medications?: string[];
  weightKg?: number;
  ageYears?: number;
  species?: string;
  breed?: string;
  noteDraftSeed?: string;
  redFlags?: string[];
  followupIntent?: string;
  operationalWindow?: string;
  inventorySignals?: string[];
}

export interface OrchestratorRequest {
  requestId: string;
  actorRole: ActorRole;
  taskType: TaskType;
  subject: OrchestratorSubjectContext;
  input: OrchestratorInputEnvelope;
}

export interface RouteDecision {
  agent: AgentKind;
  rationale: string;
}

export interface ContextAssemblyResult {
  assembledContext: Record<string, unknown>;
  redactionsApplied: string[];
}

export interface PolicyDecision {
  allowed: boolean;
  reasons: string[];
  requiredHumanReviewer: "veterinarian" | "pharmacist" | "admin" | "none";
}

export interface ModelPayload {
  systemPolicyLayer: string;
  roleLayer: string;
  contextLayer: Record<string, unknown>;
  taskLayer: {
    taskType: TaskType;
    instructions: string;
  };
}

export interface OrchestratorResult {
  requestId: string;
  route: RouteDecision;
  context: ContextAssemblyResult;
  policy: PolicyDecision;
  payload?: ModelPayload;
  blocked: boolean;
}

export class PolicyViolationError extends Error {
  public readonly reasons: string[];

  constructor(reasons: string[]) {
    super(reasons.join(" | "));
    this.name = "PolicyViolationError";
    this.reasons = reasons;
  }
}
