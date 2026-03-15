export interface LedgerValidationSummary {
  pack: "PETCARE-AI-FND-7";
  validationMode: "python_structural_runner";
  filesChecked: string[];
  requiredSymbolsConfirmed: boolean;
  notes: string[];
}

export const LEDGER_VALIDATION_SUMMARY: LedgerValidationSummary = {
  pack: "PETCARE-AI-FND-7",
  validationMode: "python_structural_runner",
  filesChecked: [
    "petcare_execution/AI_RUNTIME/runtime_ledger/AGENT_RUNTIME_LEDGER_SPEC.md",
    "petcare_execution/AI_RUNTIME/runtime_ledger/runtime_execution_ledger.ts",
    "petcare_execution/AI_RUNTIME/runtime_ledger/audit_chain_anchors.ts",
    "petcare_execution/AI_RUNTIME/runtime_ledger/release_evidence_bundle.ts",
    "petcare_execution/AI_RUNTIME/runtime_ledger/ledger_validation_pack.ts",
    "petcare_execution/AI_RUNTIME/runtime_ledger/ledger_validation_runner.py"
  ],
  requiredSymbolsConfirmed: true,
  notes: [
    "Validation intentionally avoids repo-local node package dependency.",
    "Ledger integrity and audit anchor completeness are validated structurally.",
    "Pack preserves assistive-only runtime governance."
  ]
};
