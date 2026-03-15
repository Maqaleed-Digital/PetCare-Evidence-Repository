import { LAUNCH_ACTIVATION_REGISTRY } from "./launch_activation_registry"
import { LAUNCH_DAY_ACTIVATION_CHECKLIST } from "./launch_day_activation_checklist"
import { CLINIC_SERVICES_ENABLEMENT } from "./clinic_services_enablement"
import { AI_RUNTIME_LAUNCH_STATE } from "./ai_runtime_launch_state"
import { LAUNCH_GOVERNANCE_NOTIFICATION } from "./launch_governance_notification"
import { LAUNCH_ACTIVATION_DECISION } from "./launch_activation_decision"

export function buildLaunchActivationValidationPack() {
  const requiredSymbolsConfirmed =
    LAUNCH_ACTIVATION_REGISTRY.launchActivationRegistryStatus === "ACTIVE" &&
    LAUNCH_DAY_ACTIVATION_CHECKLIST.launchDayChecklistStatus === "pass" &&
    CLINIC_SERVICES_ENABLEMENT.clinicServicesEnablementStatus === "pass" &&
    AI_RUNTIME_LAUNCH_STATE.aiRuntimeLaunchStateStatus === "pass" &&
    LAUNCH_GOVERNANCE_NOTIFICATION.launchGovernanceNotificationStatus === "recorded" &&
    typeof LAUNCH_ACTIVATION_DECISION.launchDecision === "string"

  return {
    packId: "PETCARE-CLINIC-LAUNCH-ACTIVATION",
    requiredSymbolsConfirmed,
    launchActivationRegistryStatus:
      LAUNCH_ACTIVATION_REGISTRY.launchActivationRegistryStatus,
    launchDayChecklistStatus:
      LAUNCH_DAY_ACTIVATION_CHECKLIST.launchDayChecklistStatus,
    clinicServicesEnablementStatus:
      CLINIC_SERVICES_ENABLEMENT.clinicServicesEnablementStatus,
    aiRuntimeLaunchStateStatus:
      AI_RUNTIME_LAUNCH_STATE.aiRuntimeLaunchStateStatus,
    launchGovernanceNotificationStatus:
      LAUNCH_GOVERNANCE_NOTIFICATION.launchGovernanceNotificationStatus,
    launchDecisionPresent:
      typeof LAUNCH_ACTIVATION_DECISION.launchDecision === "string",
    launchDecision:
      LAUNCH_ACTIVATION_DECISION.launchDecision,
    nextRecommendedState:
      LAUNCH_ACTIVATION_DECISION.nextRecommendedState,
  } as const
}
