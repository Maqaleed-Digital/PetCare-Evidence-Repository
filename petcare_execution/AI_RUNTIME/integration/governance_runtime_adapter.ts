import { OrchestratorResult } from "../orchestrator/types";
import { PromptPackage } from "./prompt_composer";

export interface GovernanceEvaluation {
  allowedToProceed: boolean;
  reviewRequired: boolean;
  requiredReviewer: "veterinarian" | "pharmacist" | "admin" | "none";
  loggingContract: {
    logPrompt: true;
    logResponse: true;
    logOverrideCapability: true;
  };
  reasons: string[];
}

export class GovernanceRuntimeAdapter {
  evaluate(result: OrchestratorResult, promptPackage: PromptPackage): GovernanceEvaluation {
    const reasons: string[] = [];

    if (result.blocked) {
      reasons.push("Blocked orchestrator result cannot proceed to governance-approved model invocation.");
    }

    if (!promptPackage.composedText.includes("SYSTEM POLICY")) {
      reasons.push("Prompt package is missing required system policy section.");
    }

    if (!promptPackage.composedText.includes("TASK")) {
      reasons.push("Prompt package is missing required task section.");
    }

    const reviewRequired = result.policy.requiredHumanReviewer !== "none";

    return {
      allowedToProceed: reasons.length === 0,
      reviewRequired,
      requiredReviewer: result.policy.requiredHumanReviewer,
      loggingContract: {
        logPrompt: true,
        logResponse: true,
        logOverrideCapability: true,
      },
      reasons,
    };
  }
}
