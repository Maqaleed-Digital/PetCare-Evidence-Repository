export interface ClinicActivationChecklistItem {
  control: string
  required: boolean
  satisfied: boolean
  assistiveOnly: true
}

export const CLINIC_ACTIVATION_CHECKLIST: ClinicActivationChecklistItem[] = [
  {
    control: "pilot_cohort_approved",
    required: true,
    satisfied: true,
    assistiveOnly: true
  },
  {
    control: "human_approval_enforced",
    required: true,
    satisfied: true,
    assistiveOnly: true
  },
  {
    control: "kill_switch_available",
    required: true,
    satisfied: true,
    assistiveOnly: true
  },
  {
    control: "telemetry_capture_enabled",
    required: true,
    satisfied: true,
    assistiveOnly: true
  }
]
