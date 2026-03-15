export interface RegistryValidationSummary {
  pack: "PETCARE-AI-FND-5";
  validationMode: "python_structural_runner";
  filesChecked: string[];
  requiredSymbolsConfirmed: boolean;
  notes: string[];
}

export const REGISTRY_VALIDATION_SUMMARY: RegistryValidationSummary = {
  pack: "PETCARE-AI-FND-5",
  validationMode: "python_structural_runner",
  filesChecked: [
    "petcare_execution/AI_RUNTIME/runtime_registry/AGENT_RUNTIME_REGISTRY_SPEC.md",
    "petcare_execution/AI_RUNTIME/runtime_registry/runtime_registry.ts",
    "petcare_execution/AI_RUNTIME/runtime_registry/safety_event_taxonomy.ts",
    "petcare_execution/AI_RUNTIME/runtime_registry/evidence_export_hooks.ts",
    "petcare_execution/AI_RUNTIME/runtime_registry/registry_validation_pack.ts",
    "petcare_execution/AI_RUNTIME/runtime_registry/registry_validation_runner.py"
  ],
  requiredSymbolsConfirmed: true,
  notes: [
    "Validation intentionally avoids repo-local node package dependency.",
    "Registry and taxonomy structures are deterministic.",
    "Pack preserves assistive-only runtime governance."
  ]
};
