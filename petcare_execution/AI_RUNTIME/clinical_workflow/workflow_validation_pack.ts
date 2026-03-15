export interface WorkflowValidationSummary {
  pack: "PETCARE-AI-INT-3";
  validationMode: "python_structural_runner";
  workflowsCovered: string[];
  requiredSymbolsConfirmed: boolean;
  governanceBoundary: "assistive_only";
}

export const WORKFLOW_VALIDATION_SUMMARY: WorkflowValidationSummary = {
  pack: "PETCARE-AI-INT-3",
  validationMode: "python_structural_runner",
  workflowsCovered: [
    "consultation",
    "triage_board",
    "pharmacy_review",
    "emergency"
  ],
  requiredSymbolsConfirmed: true,
  governanceBoundary: "assistive_only",
};
