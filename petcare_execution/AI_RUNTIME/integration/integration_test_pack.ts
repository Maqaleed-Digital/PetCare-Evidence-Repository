import { AgentRuntimeController } from "../orchestrator/agent_runtime_controller";
import { PromptComposer } from "./prompt_composer";
import { GovernanceRuntimeAdapter } from "./governance_runtime_adapter";
import { ModelGatewayAdapter } from "./model_gateway_adapter";
import { SYNTHETIC_REQUESTS } from "./synthetic_requests";

export interface IntegrationRunRecord {
  requestId: string;
  blocked: boolean;
  routeAgent: string;
  governanceAllowed: boolean;
  reviewRequired: boolean;
  modelStatus: "accepted" | "blocked";
}

export class AgentRuntimeIntegrationTestPack {
  private readonly controller = new AgentRuntimeController();
  private readonly composer = new PromptComposer();
  private readonly governance = new GovernanceRuntimeAdapter();
  private readonly gateway = new ModelGatewayAdapter();

  run(): IntegrationRunRecord[] {
    return SYNTHETIC_REQUESTS.map((request) => {
      const orchestratorResult = this.controller.orchestrate(request);

      if (orchestratorResult.blocked || !orchestratorResult.payload) {
        return {
          requestId: request.requestId,
          blocked: true,
          routeAgent: orchestratorResult.route.agent,
          governanceAllowed: false,
          reviewRequired: orchestratorResult.policy.requiredHumanReviewer !== "none",
          modelStatus: "blocked",
        };
      }

      const promptPackage = this.composer.compose(orchestratorResult);
      const governanceResult = this.governance.evaluate(orchestratorResult, promptPackage);
      const modelResult = this.gateway.invoke(promptPackage, governanceResult);

      return {
        requestId: request.requestId,
        blocked: false,
        routeAgent: orchestratorResult.route.agent,
        governanceAllowed: governanceResult.allowedToProceed,
        reviewRequired: governanceResult.reviewRequired,
        modelStatus: modelResult.status,
      };
    });
  }
}
