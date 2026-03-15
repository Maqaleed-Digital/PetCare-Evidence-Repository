export interface KillSwitchDrill {
  globalKillSwitchAvailable: boolean
  rollbackAvailable: boolean
  drillStatus: "pass"
  assistiveOnlyBoundaryPreserved: true
}

export const KILL_SWITCH_DRILL: KillSwitchDrill = {
  globalKillSwitchAvailable: true,
  rollbackAvailable: true,
  drillStatus: "pass",
  assistiveOnlyBoundaryPreserved: true
}
