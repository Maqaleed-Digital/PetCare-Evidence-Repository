export interface ProductionReadinessCheck {
  control: string
  required: boolean
  satisfied: boolean
  assistiveOnly: true
}

export const PRODUCTION_READINESS_CHECKLIST: ProductionReadinessCheck[] = [

{
control: "assistive_only_boundary",
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
control: "telemetry_logging_enabled",
required: true,
satisfied: true,
assistiveOnly: true
},

{
control: "pilot_governance_verified",
required: true,
satisfied: true,
assistiveOnly: true
}

]
