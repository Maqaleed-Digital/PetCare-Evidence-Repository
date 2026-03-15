export interface LaunchGovernanceExport {

pack: "PETCARE-AI-OPS-4"
exportType: "production_launch_governance"
assistiveOnlyBoundaryPreserved: true
includes: string[]

}

export function exportLaunchGovernance(): LaunchGovernanceExport {

return {

pack: "PETCARE-AI-OPS-4",

exportType: "production_launch_governance",

assistiveOnlyBoundaryPreserved: true,

includes: [

"production_launch_authorization",

"post_deployment_monitoring",

"incident_escalation_rules"

]

}

}
