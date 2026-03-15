import { KPI_REPORTING_REGISTRY } from "./kpi_reporting_registry"
import { CLINICAL_AND_SERVICE_KPI_REPORTING } from "./clinical_and_service_kpi_reporting"
import { PHARMACY_BILLING_PARTNER_KPI_REPORTING } from "./pharmacy_billing_partner_kpi_reporting"
import { AI_GOVERNANCE_AND_OVERRIDE_KPI_REPORTING } from "./ai_governance_and_override_kpi_reporting"
import { SCALE_READINESS_GOVERNANCE } from "./scale_readiness_governance"
import { GOVERNANCE_REVIEW_AND_REPORTING_CYCLE } from "./governance_review_and_reporting_cycle"
import { KPI_SCALE_GOVERNANCE_DECISION } from "./kpi_scale_governance_decision"

export function buildKpiScaleGovernanceValidationPack() {
  const requiredSymbolsConfirmed =
    KPI_REPORTING_REGISTRY.kpiReportingRegistryStatus === "ACTIVE" &&
    CLINICAL_AND_SERVICE_KPI_REPORTING.clinicalAndServiceKpiReportingStatus === "pass" &&
    PHARMACY_BILLING_PARTNER_KPI_REPORTING.pharmacyBillingPartnerKpiReportingStatus === "pass" &&
    AI_GOVERNANCE_AND_OVERRIDE_KPI_REPORTING.aiGovernanceAndOverrideKpiReportingStatus === "pass" &&
    SCALE_READINESS_GOVERNANCE.scaleReadinessGovernanceStatus === "pass" &&
    GOVERNANCE_REVIEW_AND_REPORTING_CYCLE.governanceReviewAndReportingCycleStatus === "pass" &&
    typeof KPI_SCALE_GOVERNANCE_DECISION.kpiScaleGovernanceDecision === "string"

  return {
    packId: "PETCARE-KPI-REPORTING-AND-SCALE-READINESS-GOVERNANCE",
    requiredSymbolsConfirmed,
    kpiReportingRegistryStatus:
      KPI_REPORTING_REGISTRY.kpiReportingRegistryStatus,
    clinicalAndServiceKpiReportingStatus:
      CLINICAL_AND_SERVICE_KPI_REPORTING.clinicalAndServiceKpiReportingStatus,
    pharmacyBillingPartnerKpiReportingStatus:
      PHARMACY_BILLING_PARTNER_KPI_REPORTING.pharmacyBillingPartnerKpiReportingStatus,
    aiGovernanceAndOverrideKpiReportingStatus:
      AI_GOVERNANCE_AND_OVERRIDE_KPI_REPORTING.aiGovernanceAndOverrideKpiReportingStatus,
    scaleReadinessGovernanceStatus:
      SCALE_READINESS_GOVERNANCE.scaleReadinessGovernanceStatus,
    governanceReviewAndReportingCycleStatus:
      GOVERNANCE_REVIEW_AND_REPORTING_CYCLE.governanceReviewAndReportingCycleStatus,
    kpiScaleGovernanceDecisionPresent:
      typeof KPI_SCALE_GOVERNANCE_DECISION.kpiScaleGovernanceDecision === "string",
    kpiScaleGovernanceDecision:
      KPI_SCALE_GOVERNANCE_DECISION.kpiScaleGovernanceDecision,
    nextRecommendedState:
      KPI_SCALE_GOVERNANCE_DECISION.nextRecommendedState,
  } as const
}
