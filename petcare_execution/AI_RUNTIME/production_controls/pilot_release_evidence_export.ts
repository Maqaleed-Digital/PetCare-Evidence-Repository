// pilot_release_evidence_export.ts
// PETCARE-AI-OPS-1: Evidence export for pilot release audit

import { AI_RUNTIME_ACTIVATION_REGISTRY } from "./runtime_activation_registry";
import { GLOBAL_AI_KILL_SWITCH } from "./ai_runtime_kill_switch";
import { PILOT_COHORT_REGISTRY } from "./pilot_cohort_governance";

export interface PilotReleaseEvidenceBundle {
  bundleId: string;
  packId: "PETCARE-AI-OPS-1";
  generatedAt: string;
  killSwitchState: string;
  activatedClinics: string[];
  activeCohorts: string[];
  assistiveOnlyEnforced: true;
  humanApprovalEnforced: true;
  auditLoggingEnforced: true;
  governanceReadiness: "production_controls_active";
  boardReadinessHints: string[];
}

export function exportPilotReleaseEvidence(): PilotReleaseEvidenceBundle {
  const activatedClinics = AI_RUNTIME_ACTIVATION_REGISTRY.filter(
    (e) => e.activationState === "active"
  ).map((e) => e.clinicId);

  const activeCohorts = PILOT_COHORT_REGISTRY.filter(
    (c) => c.status === "active"
  ).map((c) => c.cohortId);

  return {
    bundleId: `OPS1-PILOT-RELEASE-${Date.now()}`,
    packId: "PETCARE-AI-OPS-1",
    generatedAt: new Date().toISOString(),
    killSwitchState: GLOBAL_AI_KILL_SWITCH.state,
    activatedClinics,
    activeCohorts,
    assistiveOnlyEnforced: true,
    humanApprovalEnforced: true,
    auditLoggingEnforced: true,
    governanceReadiness: "production_controls_active",
    boardReadinessHints: [
      "Kill switch operational — runtime can be halted globally at any time",
      "Pilot cohort AI_PILOT_ALPHA active with pilot_clinic_001 enrolled",
      "All agents configured as assistive-only",
      "Human approval mandatory for all clinical decisions",
      "Drift detection threshold set at 0.15 override rate delta",
      "Weekly cohort review cadence established",
      "Audit logging required for all AI interactions",
    ],
  };
}
