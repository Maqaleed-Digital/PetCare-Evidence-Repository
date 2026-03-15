export interface PostDeploymentMonitoring {

monitoringEnabled: boolean
safetyMonitoring: boolean
driftMonitoring: boolean
assistiveOnlyBoundaryPreserved: true

}

export const POST_DEPLOYMENT_MONITORING: PostDeploymentMonitoring = {

monitoringEnabled: true,

safetyMonitoring: true,

driftMonitoring: true,

assistiveOnlyBoundaryPreserved: true

}
