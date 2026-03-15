import { OrchestratorResult } from "../orchestrator/types";
import { PromptPackage } from "../integration/prompt_composer";
import { GovernanceEvaluation } from "../integration/governance_runtime_adapter";
import { SyntheticModelResponse } from "../integration/model_gateway_adapter";

export interface RuntimeLogEvent {
  eventType: "prompt_logged" | "response_logged" | "decision_logged";
  requestId: string;
  routeAgent: string;
  reviewRequired: boolean;
  reviewer: "veterinarian" | "pharmacist" | "admin" | "none";
  blocked: boolean;
  details: Record<string, unknown>;
}

export class RuntimeEventLogger {
  buildPromptLog(
    result: OrchestratorResult,
    promptPackage: PromptPackage,
    governance: GovernanceEvaluation,
  ): RuntimeLogEvent {
    return {
      eventType: "prompt_logged",
      requestId: result.requestId,
      routeAgent: result.route.agent,
      reviewRequired: governance.reviewRequired,
      reviewer: governance.requiredReviewer,
      blocked: result.blocked,
      details: {
        promptId: promptPackage.promptId,
        taskType: promptPackage.task.type,
        loggingContract: governance.loggingContract,
      },
    };
  }

  buildResponseLog(
    result: OrchestratorResult,
    response: SyntheticModelResponse,
    governance: GovernanceEvaluation,
  ): RuntimeLogEvent {
    return {
      eventType: "response_logged",
      requestId: result.requestId,
      routeAgent: result.route.agent,
      reviewRequired: governance.reviewRequired,
      reviewer: governance.requiredReviewer,
      blocked: response.status === "blocked",
      details: {
        gatewayRequestId: response.gatewayRequestId,
        model: response.model,
        status: response.status,
        summary: response.output.summary,
      },
    };
  }

  buildDecisionLog(
    result: OrchestratorResult,
    governance: GovernanceEvaluation,
  ): RuntimeLogEvent {
    return {
      eventType: "decision_logged",
      requestId: result.requestId,
      routeAgent: result.route.agent,
      reviewRequired: governance.reviewRequired,
      reviewer: governance.requiredReviewer,
      blocked: !governance.allowedToProceed,
      details: {
        reasons: governance.reasons,
        allowedToProceed: governance.allowedToProceed,
      },
    };
  }
}
