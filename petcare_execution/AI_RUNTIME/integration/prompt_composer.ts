import { ModelPayload, OrchestratorResult } from "../orchestrator/types";

export interface PromptPackage {
  promptId: string;
  system: string;
  role: string;
  context: Record<string, unknown>;
  task: {
    type: string;
    instructions: string;
  };
  composedText: string;
}

export class PromptComposer {
  compose(result: OrchestratorResult): PromptPackage {
    if (result.blocked || !result.payload) {
      throw new Error("Cannot compose prompt package for blocked or payload-less result.");
    }

    const payload: ModelPayload = result.payload;
    const composedText = [
      "SYSTEM POLICY",
      payload.systemPolicyLayer,
      "",
      "ROLE",
      payload.roleLayer,
      "",
      "CONTEXT",
      JSON.stringify(payload.contextLayer, null, 2),
      "",
      "TASK",
      `type=${payload.taskLayer.taskType}`,
      payload.taskLayer.instructions,
    ].join("\n");

    return {
      promptId: `prompt_${result.requestId}`,
      system: payload.systemPolicyLayer,
      role: payload.roleLayer,
      context: payload.contextLayer,
      task: {
        type: payload.taskLayer.taskType,
        instructions: payload.taskLayer.instructions,
      },
      composedText,
    };
  }
}
