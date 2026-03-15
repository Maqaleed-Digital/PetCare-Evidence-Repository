// ai_runtime_kill_switch.ts
// PETCARE-AI-OPS-1: Global AI runtime kill switch

export type KillSwitchState = "ACTIVE" | "HALTED";

export interface KillSwitchRecord {
  switchId: string;
  state: KillSwitchState;
  reason: string;
  setAt: string;
  setBy: string;
  affectsAllClinics: true;
  affectsAllAgents: true;
}

export const GLOBAL_AI_KILL_SWITCH: KillSwitchRecord = {
  switchId: "GLOBAL_AI_KILL_SWITCH",
  state: "ACTIVE",
  reason: "Initial production activation — pilot cohort AI_PILOT_ALPHA",
  setAt: "2025-01-01T00:00:00Z",
  setBy: "governance_board",
  affectsAllClinics: true,
  affectsAllAgents: true,
};

export function isAIRuntimeAllowed(): boolean {
  return GLOBAL_AI_KILL_SWITCH.state === "ACTIVE";
}

export function getKillSwitchState(): KillSwitchState {
  return GLOBAL_AI_KILL_SWITCH.state;
}

export function assertAIRuntimeAllowed(): void {
  if (!isAIRuntimeAllowed()) {
    throw new Error(
      `AI runtime is HALTED. Kill switch state: ${GLOBAL_AI_KILL_SWITCH.state}. Reason: ${GLOBAL_AI_KILL_SWITCH.reason}`
    );
  }
}
