import { AgentRouter } from "./agent_router";
import { ContextAssembler } from "./context_assembler";
import { PolicyEnforcer } from "./policy_enforcer";
import {
  ModelPayload,
  OrchestratorRequest,
  OrchestratorResult,
  PolicyViolationError,
} from "./types";

export class AgentRuntimeController {
  private readonly router = new AgentRouter();
  private readonly contextAssembler = new ContextAssembler();
  private readonly policyEnforcer = new PolicyEnforcer();

  orchestrate(request: OrchestratorRequest): OrchestratorResult {
    const route = this.router.route(request.taskType);
    const context = this.contextAssembler.assemble(request);
    const policy = this.policyEnforcer.evaluate(request, context.assembledContext);

    if (!policy.allowed) {
      return {
        requestId: request.requestId,
        route,
        context,
        policy,
        blocked: true,
      };
    }

    const payload = this.buildPayload(request, context.assembledContext);

    return {
      requestId: request.requestId,
      route,
      context,
      policy,
      payload,
      blocked: false,
    };
  }

  assertAllowed(result: OrchestratorResult): void {
    if (result.blocked) {
      throw new PolicyViolationError(result.policy.reasons);
    }
  }

  private buildPayload(
    request: OrchestratorRequest,
    contextLayer: Record<string, unknown>,
  ): ModelPayload {
    return {
      systemPolicyLayer:
        "Assistive-only veterinary AI. No diagnosis finalization. No prescriptions. No treatment authorization. No consultation closure. Human review required where indicated.",
      roleLayer: this.buildRoleLayer(request.actorRole),
      contextLayer,
      taskLayer: {
        taskType: request.taskType,
        instructions: this.buildTaskInstruction(request.taskType),
      },
    };
  }

  private buildRoleLayer(role: OrchestratorRequest["actorRole"]): string {
    switch (role) {
      case "veterinarian":
        return "You are assisting a licensed veterinarian with governed draft support only.";
      case "pharmacy_operator":
        return "You are assisting a pharmacy operator with safety review support only.";
      case "partner_admin":
        return "You are assisting a clinic admin with governed operational support only.";
      case "platform_admin":
        return "You are assisting a platform admin with governance-safe operational support only.";
      case "owner":
      default:
        return "You are assisting an end user with non-authoritative informational support only.";
    }
  }

  private buildTaskInstruction(taskType: OrchestratorRequest["taskType"]): string {
    switch (taskType) {
      case "summarize_history":
        return "Summarize longitudinal health context and highlight clinically relevant factors without making final decisions.";
      case "draft_consult_note":
        return "Draft a structured consultation note for veterinarian review and sign-off.";
      case "medication_safety_review":
        return "Review medication context for interactions, contraindications, and anomalies with clear uncertainty.";
      case "emergency_intake_support":
        return "Support emergency intake by organizing symptoms, red flags, and stabilization prompts for clinician review.";
      case "operations_forecast":
        return "Provide operational demand and scheduling support using the supplied signals only.";
      case "client_followup_draft":
        return "Draft a client-friendly follow-up communication using approved, non-diagnostic wording.";
      default:
        return "Provide governed assistive support.";
    }
  }
}
