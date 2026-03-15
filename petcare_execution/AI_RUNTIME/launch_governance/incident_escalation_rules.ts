export interface IncidentEscalationRule {

trigger: string
severity: string
action: string
assistiveOnly: true

}

export const INCIDENT_ESCALATION_RULES: IncidentEscalationRule[] = [

{
trigger: "safety_breach",
severity: "critical",
action: "immediate_freeze",
assistiveOnly: true
},

{
trigger: "behavioral_drift",
severity: "high",
action: "review_required",
assistiveOnly: true
}

]
