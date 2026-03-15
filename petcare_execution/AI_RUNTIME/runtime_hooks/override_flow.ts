import { OrchestratorResult } from "../orchestrator/types";
import { GovernanceEvaluation } from "../integration/governance_runtime_adapter";

export interface OverrideRequest {
  requestId: string;
  requestedByRole: string;
  reasonCode: string;
  note: string;
}

export interface OverrideRecord {
  requestId: string;
  allowedToRequestOverride: boolean;
  requiredReviewer: "veterinarian" | "pharmacist" | "admin" | "none";
  reasonCode: string;
  note: string;
  escalationRequired: boolean;
}

export class OverrideFlow {
  createRecord(
    result: OrchestratorResult,
    governance: GovernanceEvaluation,
    request: OverrideRequest,
  ): OverrideRecord {
    const allowedToRequestOverride =
      request.requestId === result.requestId &&
      governance.requiredReviewer !== "none";

    return {
      requestId: result.requestId,
      allowedToRequestOverride,
      requiredReviewer: governance.requiredReviewer,
      reasonCode: request.reasonCode.trim(),
      note: request.note.trim(),
      escalationRequired: governance.requiredReviewer !== "none",
    };
  }
}
