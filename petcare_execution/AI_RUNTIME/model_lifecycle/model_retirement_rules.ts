export interface ModelRetirementRule {

trigger: string
action: string
assistiveOnly: true

}

export const MODEL_RETIREMENT_RULES: ModelRetirementRule[] = [

{
trigger: "safety_violation",
action: "retire_model",
assistiveOnly: true
},

{
trigger: "superseded_by_new_version",
action: "archive_model",
assistiveOnly: true
}

]
