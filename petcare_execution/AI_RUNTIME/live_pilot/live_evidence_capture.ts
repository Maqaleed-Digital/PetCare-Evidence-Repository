export interface LiveEvidenceCapture {
  pack: "PETCARE-AI-LIVE-1"
  exportType: "controlled_live_pilot_evidence"
  assistiveOnlyBoundaryPreserved: true
  includes: string[]
}

export function exportLivePilotEvidence(): LiveEvidenceCapture {
  return {
    pack: "PETCARE-AI-LIVE-1",
    exportType: "controlled_live_pilot_evidence",
    assistiveOnlyBoundaryPreserved: true,
    includes: [
      "pilot_activation_plan",
      "clinic_activation_checklist",
      "human_approval_enforcement",
      "kill_switch_drill"
    ]
  }
}
