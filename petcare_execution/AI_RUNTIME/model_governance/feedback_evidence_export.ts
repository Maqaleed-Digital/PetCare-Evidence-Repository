export interface FeedbackEvidenceExport {
  exportType: "feedback_governance_summary";
  pack: "PETCARE-AI-INT-6";
  assistiveOnlyBoundaryPreserved: true;
  includes: string[];
}

export function exportFeedbackEvidence(): FeedbackEvidenceExport {
  return {
    exportType: "feedback_governance_summary",
    pack: "PETCARE-AI-INT-6",
    assistiveOnlyBoundaryPreserved: true,
    includes: [
      "clinician_feedback_capture",
      "model_performance_scoring",
      "governance_review_signals",
      "prompt_refinement_pipeline"
    ],
  };
}
