export interface PolicyValidationSummary {
  pack: "PETCARE-AI-FND-6";
  validationMode: "python_structural_runner";
  filesChecked: string[];
  requiredSymbolsConfirmed: boolean;
  notes: string[];
}

export const POLICY_VALIDATION_SUMMARY: PolicyValidationSummary = {
  pack: "PETCARE-AI-FND-6",
  validationMode: "python_structural_runner",
  filesChecked: [
    "petcare_execution/AI_RUNTIME/runtime_policy/AGENT_RUNTIME_POLICY_SPEC.md",
    "petcare_execution/AI_RUNTIME/runtime_policy/runtime_policy_bundles.ts",
    "petcare_execution/AI_RUNTIME/runtime_policy/prompt_registry_binding.ts",
    "petcare_execution/AI_RUNTIME/runtime_policy/audit_bundle_export.ts",
    "petcare_execution/AI_RUNTIME/runtime_policy/policy_validation_pack.ts",
    "petcare_execution/AI_RUNTIME/runtime_policy/policy_validation_runner.py"
  ],
  requiredSymbolsConfirmed: true,
  notes: [
    "Validation intentionally avoids repo-local node package dependency.",
    "Policy bundles and prompt bindings are deterministic.",
    "Pack preserves assistive-only runtime governance."
  ]
};
