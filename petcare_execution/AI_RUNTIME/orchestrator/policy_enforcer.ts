import {
  ActorRole,
  OrchestratorRequest,
  PolicyDecision,
} from "./types";

const FORBIDDEN_PATTERNS: RegExp[] = [
  /\bdiagnose\b/i,
  /\bfinal diagnosis\b/i,
  /\bprescribe\b/i,
  /\bissue prescription\b/i,
  /\bauthorize treatment\b/i,
  /\bfinalize triage\b/i,
  /\bclose consultation\b/i,
  /\bsign medical record\b/i,
];

export class PolicyEnforcer {
  evaluate(request: OrchestratorRequest, assembledContext: Record<string, unknown>): PolicyDecision {
    const reasons: string[] = [];

    const flattened = JSON.stringify({
      taskType: request.taskType,
      input: request.input,
      assembledContext,
    });

    for (const pattern of FORBIDDEN_PATTERNS) {
      if (pattern.test(flattened)) {
        reasons.push(`Forbidden autonomous clinical intent matched: ${pattern.toString()}`);
      }
    }

    const requiredHumanReviewer = this.getRequiredReviewer(request.actorRole, request.taskType);

    if (request.taskType === "draft_consult_note" && request.actorRole !== "veterinarian") {
      reasons.push("Only a veterinarian may initiate clinical consult note drafting context.");
    }

    if (request.taskType === "medication_safety_review" && !this.isMedicationRoleAllowed(request.actorRole)) {
      reasons.push("Medication safety review requires veterinarian or pharmacy operator role.");
    }

    if (request.taskType === "emergency_intake_support" && request.actorRole === "owner") {
      reasons.push("Emergency intake support cannot be finalized from owner role without clinician review.");
    }

    return {
      allowed: reasons.length === 0,
      reasons,
      requiredHumanReviewer,
    };
  }

  private getRequiredReviewer(
    actorRole: ActorRole,
    taskType: OrchestratorRequest["taskType"],
  ): PolicyDecision["requiredHumanReviewer"] {
    if (taskType === "medication_safety_review") {
      return "pharmacist";
    }
    if (taskType === "summarize_history" || taskType === "draft_consult_note" || taskType === "emergency_intake_support") {
      return "veterinarian";
    }
    if (taskType === "operations_forecast") {
      return actorRole === "platform_admin" ? "admin" : "none";
    }
    if (taskType === "client_followup_draft") {
      return "none";
    }
    return "none";
  }

  private isMedicationRoleAllowed(actorRole: ActorRole): boolean {
    return actorRole === "veterinarian" || actorRole === "pharmacy_operator";
  }
}
