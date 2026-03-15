export function evaluationSummaryExport(metrics) {

  return {
    report: "ai_evaluation_summary",
    agents: metrics,
    generatedAt: new Date().toISOString()
  };

}
