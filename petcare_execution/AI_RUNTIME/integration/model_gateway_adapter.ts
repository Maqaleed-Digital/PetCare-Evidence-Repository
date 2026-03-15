import { PromptPackage } from "./prompt_composer";
import { GovernanceEvaluation } from "./governance_runtime_adapter";

export interface SyntheticModelResponse {
  gatewayRequestId: string;
  model: string;
  status: "accepted" | "blocked";
  output: {
    summary: string;
    disclaimer: string;
    reviewRequired: boolean;
  };
}

export class ModelGatewayAdapter {
  invoke(promptPackage: PromptPackage, governance: GovernanceEvaluation): SyntheticModelResponse {
    if (!governance.allowedToProceed) {
      return {
        gatewayRequestId: `gw_${promptPackage.promptId}`,
        model: "synthetic-governed-model",
        status: "blocked",
        output: {
          summary: "Invocation blocked by governance runtime.",
          disclaimer: "No model output available because governance approval failed.",
          reviewRequired: governance.reviewRequired,
        },
      };
    }

    return {
      gatewayRequestId: `gw_${promptPackage.promptId}`,
      model: "synthetic-governed-model",
      status: "accepted",
      output: {
        summary: "Synthetic assistive response generated for governed integration verification.",
        disclaimer: "Assistive only. Human authority remains mandatory for clinical and regulated decisions.",
        reviewRequired: governance.reviewRequired,
      },
    };
  }
}
