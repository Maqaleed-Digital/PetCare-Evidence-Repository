export interface PilotMonitoringExport {
  pack: "PETCARE-AI-OPS-2"
  exportType: "pilot_monitoring_summary"
  assistiveOnlyBoundaryPreserved: true
  includes: string[]
}

export function exportPilotMonitoring(): PilotMonitoringExport {

  return {
    pack: "PETCARE-AI-OPS-2",
    exportType: "pilot_monitoring_summary",
    assistiveOnlyBoundaryPreserved: true,
    includes: [
      "pilot_monitoring_signals",
      "clinical_safety_review",
      "deployment_approval_gates"
    ]
  }
}
