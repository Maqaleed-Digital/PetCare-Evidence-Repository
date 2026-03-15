import { LIVE_OPERATIONS_REGISTRY } from "./live_operations_registry"
import { CLINICAL_SERVICE_MONITORING } from "./clinical_service_monitoring"
import { PHARMACY_OPERATIONS_MONITORING } from "./pharmacy_operations_monitoring"
import { BILLING_PARTNER_OPERATIONS_MONITORING } from "./billing_partner_operations_monitoring"
import { AI_GOVERNANCE_LIVE_MONITORING } from "./ai_governance_live_monitoring"
import { INCIDENT_ESCALATION_AND_SHIFT_HANDOVER } from "./incident_escalation_and_shift_handover"
import { LIVE_OPERATIONS_DECISION } from "./live_operations_decision"

export function buildLiveOperationsValidationPack() {
  const requiredSymbolsConfirmed =
    LIVE_OPERATIONS_REGISTRY.liveOperationsRegistryStatus === "ACTIVE" &&
    CLINICAL_SERVICE_MONITORING.clinicalServiceMonitoringStatus === "pass" &&
    PHARMACY_OPERATIONS_MONITORING.pharmacyOperationsMonitoringStatus === "pass" &&
    BILLING_PARTNER_OPERATIONS_MONITORING.billingPartnerOperationsMonitoringStatus === "pass" &&
    AI_GOVERNANCE_LIVE_MONITORING.aiGovernanceLiveMonitoringStatus === "pass" &&
    INCIDENT_ESCALATION_AND_SHIFT_HANDOVER.incidentEscalationAndShiftHandoverStatus === "pass" &&
    typeof LIVE_OPERATIONS_DECISION.liveOperationsDecision === "string"

  return {
    packId: "PETCARE-CLINIC-LIVE-OPERATIONS",
    requiredSymbolsConfirmed,
    liveOperationsRegistryStatus:
      LIVE_OPERATIONS_REGISTRY.liveOperationsRegistryStatus,
    clinicalServiceMonitoringStatus:
      CLINICAL_SERVICE_MONITORING.clinicalServiceMonitoringStatus,
    pharmacyOperationsMonitoringStatus:
      PHARMACY_OPERATIONS_MONITORING.pharmacyOperationsMonitoringStatus,
    billingPartnerOperationsMonitoringStatus:
      BILLING_PARTNER_OPERATIONS_MONITORING.billingPartnerOperationsMonitoringStatus,
    aiGovernanceLiveMonitoringStatus:
      AI_GOVERNANCE_LIVE_MONITORING.aiGovernanceLiveMonitoringStatus,
    incidentEscalationAndShiftHandoverStatus:
      INCIDENT_ESCALATION_AND_SHIFT_HANDOVER.incidentEscalationAndShiftHandoverStatus,
    liveOperationsDecisionPresent:
      typeof LIVE_OPERATIONS_DECISION.liveOperationsDecision === "string",
    liveOperationsDecision:
      LIVE_OPERATIONS_DECISION.liveOperationsDecision,
    nextRecommendedState:
      LIVE_OPERATIONS_DECISION.nextRecommendedState,
  } as const
}
