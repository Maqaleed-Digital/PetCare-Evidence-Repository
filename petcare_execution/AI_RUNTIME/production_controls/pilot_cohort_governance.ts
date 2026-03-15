// pilot_cohort_governance.ts
// PETCARE-AI-OPS-1: Pilot cohort registry and governance rules

export type CohortStatus = "active" | "paused" | "graduated" | "terminated";

export interface PilotCohortEntry {
  cohortId: string;
  cohortName: string;
  status: CohortStatus;
  enrolledClinics: string[];
  governanceRules: CohortGovernanceRules;
  enrolledAt: string;
  reviewCadence: string;
}

export interface CohortGovernanceRules {
  assistiveOnly: true;
  humanApprovalMandatory: true;
  maxOverrideRateBeforePause: number;
  maxSafetyFlagsBeforePause: number;
  minPositiveFeedbackRateForGraduation: number;
  auditLoggingRequired: true;
  driftThreshold: number;
}

export const PILOT_COHORT_REGISTRY: PilotCohortEntry[] = [
  {
    cohortId: "AI_PILOT_ALPHA",
    cohortName: "PetCare AI Pilot Alpha Cohort",
    status: "active",
    enrolledClinics: ["pilot_clinic_001"],
    governanceRules: {
      assistiveOnly: true,
      humanApprovalMandatory: true,
      maxOverrideRateBeforePause: 0.2,
      maxSafetyFlagsBeforePause: 5,
      minPositiveFeedbackRateForGraduation: 0.75,
      auditLoggingRequired: true,
      driftThreshold: 0.15,
    },
    enrolledAt: "2025-01-01T00:00:00Z",
    reviewCadence: "weekly",
  },
];

export function getCohortEntry(cohortId: string): PilotCohortEntry | undefined {
  return PILOT_COHORT_REGISTRY.find((c) => c.cohortId === cohortId);
}

export function isCohortActive(cohortId: string): boolean {
  const entry = getCohortEntry(cohortId);
  return entry?.status === "active" ?? false;
}

export function isClinicEnrolled(
  cohortId: string,
  clinicId: string
): boolean {
  const entry = getCohortEntry(cohortId);
  return entry?.enrolledClinics.includes(clinicId) ?? false;
}
