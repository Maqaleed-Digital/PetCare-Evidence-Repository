// runtime_activation_registry.ts
// PETCARE-AI-OPS-1: Production activation registry for AI runtime

export type ActivationState = "active" | "inactive" | "suspended";

export interface RuntimeActivationEntry {
  clinicId: string;
  clinicName: string;
  activationState: ActivationState;
  assistiveOnly: true;
  activatedAt: string;
  activatedBy: string;
  pilotCohort: string;
  enabledAgents: string[];
  humanApprovalRequired: true;
  auditLoggingEnabled: true;
}

export const AI_RUNTIME_ACTIVATION_REGISTRY: RuntimeActivationEntry[] = [
  {
    clinicId: "pilot_clinic_001",
    clinicName: "PetCare Pilot Clinic Alpha",
    activationState: "active",
    assistiveOnly: true,
    activatedAt: "2025-01-01T00:00:00Z",
    activatedBy: "governance_board",
    pilotCohort: "AI_PILOT_ALPHA",
    enabledAgents: [
      "clinical_copilot_agent",
      "triage_support_agent",
      "prescription_safety_agent",
      "pharmacy_inventory_agent",
      "emergency_coordination_agent",
    ],
    humanApprovalRequired: true,
    auditLoggingEnabled: true,
  },
];

export function getActivationEntry(
  clinicId: string
): RuntimeActivationEntry | undefined {
  return AI_RUNTIME_ACTIVATION_REGISTRY.find((e) => e.clinicId === clinicId);
}

export function isClinicActivated(clinicId: string): boolean {
  const entry = getActivationEntry(clinicId);
  return entry?.activationState === "active" ?? false;
}
