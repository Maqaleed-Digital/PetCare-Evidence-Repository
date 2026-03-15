export interface PromotionReadinessExport {
  pack: "PETCARE-AI-INT-7";
  exportType: "promotion_readiness_summary";
  assistiveOnlyBoundaryPreserved: true;
  includes: string[];
}

export function exportPromotionReadiness(): PromotionReadinessExport {
  return {
    pack: "PETCARE-AI-INT-7",
    exportType: "promotion_readiness_summary",
    assistiveOnlyBoundaryPreserved: true,
    includes: [
      "governance_dashboard_metrics",
      "agent_quality_thresholds",
      "deployment_promotion_signals"
    ]
  };
}
