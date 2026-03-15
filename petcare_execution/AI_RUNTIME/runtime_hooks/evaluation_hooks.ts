import { OrchestratorResult } from "../orchestrator/types";
import { GovernanceEvaluation } from "../integration/governance_runtime_adapter";
import { SyntheticModelResponse } from "../integration/model_gateway_adapter";

export interface EvaluationRecord {
  requestId: string;
  taskType: string;
  routeAgent: string;
  blocked: boolean;
  governanceAllowed: boolean;
  reviewRequired: boolean;
  safetyPosture: "assistive_only" | "blocked";
  responseStatus: "accepted" | "blocked";
}

export class EvaluationHooks {
  buildRecord(
    result: OrchestratorResult,
    governance: GovernanceEvaluation,
    response: SyntheticModelResponse,
  ): EvaluationRecord {
    return {
      requestId: result.requestId,
      taskType: result.payload ? result.payload.taskLayer.taskType : "blocked_before_payload",
      routeAgent: result.route.agent,
      blocked: result.blocked,
      governanceAllowed: governance.allowedToProceed,
      reviewRequired: governance.reviewRequired,
      safetyPosture: governance.allowedToProceed ? "assistive_only" : "blocked",
      responseStatus: response.status,
    };
  }
}
