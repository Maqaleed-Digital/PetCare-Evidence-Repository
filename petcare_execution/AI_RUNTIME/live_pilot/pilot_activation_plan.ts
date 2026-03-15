export interface PilotActivationPlan {
  clinicId: string
  cohort: string
  aiActivationApproved: boolean
  surfaces: string[]
  assistiveOnly: true
}

export const PILOT_ACTIVATION_PLAN: PilotActivationPlan = {
  clinicId: "pilot_clinic_001",
  cohort: "AI_PILOT_ALPHA",
  aiActivationApproved: true,
  surfaces: [
    "consultation",
    "triage",
    "pharmacy_review",
    "emergency"
  ],
  assistiveOnly: true
}
