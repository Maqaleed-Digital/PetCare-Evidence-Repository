export interface ModelGovernanceValidationSummary {
  pack: "PETCARE-AI-INT-6";
  validationMode: "python_structural_runner";
  modules: string[];
  requiredSymbolsConfirmed: boolean;
  governanceBoundary: "assistive_only";
}

export const MODEL_GOVERNANCE_VALIDATION_SUMMARY: ModelGovernanceValidationSummary = {
  pack: "PETCARE-AI-INT-6",
  validationMode: "python_structural_runner",
  modules: [
    "clinician_feedback_capture",
    "model_performance_scoring",
    "governance_review_signals",
    "prompt_refinement_pipeline",
    "feedback_evidence_export"
  ],
  requiredSymbolsConfirmed: true,
  governanceBoundary: "assistive_only",
};
