// production_controls_validation_pack.ts
// PETCARE-AI-OPS-1: Structural validation pack (validated by Python runner)

export const PRODUCTION_CONTROLS_VALIDATION_SUMMARY = {
  packId: "PETCARE-AI-OPS-1",
  validationMode: "python_structural_runner",
  validatedFiles: [
    "runtime_activation_registry.ts",
    "ai_runtime_kill_switch.ts",
    "pilot_cohort_governance.ts",
    "pilot_release_evidence_export.ts",
  ],
  requiredSymbols: {
    "runtime_activation_registry.ts": [
      "AI_RUNTIME_ACTIVATION_REGISTRY",
      "isClinicActivated",
      "getActivationEntry",
      "assistiveOnly",
      "humanApprovalRequired",
      "auditLoggingEnabled",
    ],
    "ai_runtime_kill_switch.ts": [
      "GLOBAL_AI_KILL_SWITCH",
      "isAIRuntimeAllowed",
      "assertAIRuntimeAllowed",
      "getKillSwitchState",
      "ACTIVE",
      "HALTED",
    ],
    "pilot_cohort_governance.ts": [
      "PILOT_COHORT_REGISTRY",
      "AI_PILOT_ALPHA",
      "isCohortActive",
      "isClinicEnrolled",
      "assistiveOnly",
      "humanApprovalMandatory",
    ],
    "pilot_release_evidence_export.ts": [
      "exportPilotReleaseEvidence",
      "PilotReleaseEvidenceBundle",
      "governanceReadiness",
      "boardReadinessHints",
    ],
  },
  assistiveOnlyAsserted: true,
  humanApprovalAsserted: true,
  killSwitchAsserted: true,
  auditLoggingAsserted: true,
} as const;
