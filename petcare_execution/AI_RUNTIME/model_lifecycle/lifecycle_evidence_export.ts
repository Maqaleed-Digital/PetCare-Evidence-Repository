export interface LifecycleEvidenceExport {

pack: "PETCARE-AI-OPS-5"
exportType: "model_lifecycle_governance"
assistiveOnlyBoundaryPreserved: true
includes: string[]

}

export function exportModelLifecycleGovernance(): LifecycleEvidenceExport {

return {

pack: "PETCARE-AI-OPS-5",

exportType: "model_lifecycle_governance",

assistiveOnlyBoundaryPreserved: true,

includes: [

"model_lifecycle_state_machine",

"model_promotion_rules",

"model_retirement_rules"

]

}

}
