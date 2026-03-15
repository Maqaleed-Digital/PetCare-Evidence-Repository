export interface MonitoringEvidenceExport {
  pack: "PETCARE-AI-INT-8"
  exportType: "operational_monitoring_summary"
  assistiveOnlyBoundaryPreserved: true
  includes: string[]
}

export function exportMonitoringEvidence(): MonitoringEvidenceExport {

  return {
    pack: "PETCARE-AI-INT-8",
    exportType: "operational_monitoring_summary",
    assistiveOnlyBoundaryPreserved: true,
    includes: [
      "drift_detection_engine",
      "safety_guardrail_classifier",
      "escalation_freeze_signals"
    ]
  }
}
