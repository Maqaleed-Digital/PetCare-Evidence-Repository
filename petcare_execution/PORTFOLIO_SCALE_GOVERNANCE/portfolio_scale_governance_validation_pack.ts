import { PORTFOLIO_REPORTING_REGISTRY } from "./portfolio_reporting_registry"
import { MULTI_CLINIC_OPERATING_MODEL_GOVERNANCE } from "./multi_clinic_operating_model_governance"
import { PORTFOLIO_KPI_AND_BOARD_REPORTING } from "./portfolio_kpi_and_board_reporting"
import { CLINIC_REPLICATION_READINESS_GOVERNANCE } from "./clinic_replication_readiness_governance"
import { AI_GOVERNANCE_SCALE_CONTROLS } from "./ai_governance_scale_controls"
import { NETWORK_RISK_AND_COMPLIANCE_GOVERNANCE } from "./network_risk_and_compliance_governance"
import { PORTFOLIO_SCALE_GOVERNANCE_DECISION } from "./portfolio_scale_governance_decision"

export function buildPortfolioScaleGovernanceValidationPack() {
  const requiredSymbolsConfirmed =
    PORTFOLIO_REPORTING_REGISTRY.portfolioReportingRegistryStatus === "ACTIVE" &&
    MULTI_CLINIC_OPERATING_MODEL_GOVERNANCE.multiClinicOperatingModelGovernanceStatus === "pass" &&
    PORTFOLIO_KPI_AND_BOARD_REPORTING.portfolioKpiAndBoardReportingStatus === "pass" &&
    CLINIC_REPLICATION_READINESS_GOVERNANCE.clinicReplicationReadinessGovernanceStatus === "pass" &&
    AI_GOVERNANCE_SCALE_CONTROLS.aiGovernanceScaleControlsStatus === "pass" &&
    NETWORK_RISK_AND_COMPLIANCE_GOVERNANCE.networkRiskAndComplianceGovernanceStatus === "pass" &&
    typeof PORTFOLIO_SCALE_GOVERNANCE_DECISION.portfolioScaleGovernanceDecision === "string"

  return {
    packId: "PETCARE-PORTFOLIO-REPORTING-AND-MULTI-CLINIC-SCALE-GOVERNANCE",
    requiredSymbolsConfirmed,
    portfolioReportingRegistryStatus:
      PORTFOLIO_REPORTING_REGISTRY.portfolioReportingRegistryStatus,
    multiClinicOperatingModelGovernanceStatus:
      MULTI_CLINIC_OPERATING_MODEL_GOVERNANCE.multiClinicOperatingModelGovernanceStatus,
    portfolioKpiAndBoardReportingStatus:
      PORTFOLIO_KPI_AND_BOARD_REPORTING.portfolioKpiAndBoardReportingStatus,
    clinicReplicationReadinessGovernanceStatus:
      CLINIC_REPLICATION_READINESS_GOVERNANCE.clinicReplicationReadinessGovernanceStatus,
    aiGovernanceScaleControlsStatus:
      AI_GOVERNANCE_SCALE_CONTROLS.aiGovernanceScaleControlsStatus,
    networkRiskAndComplianceGovernanceStatus:
      NETWORK_RISK_AND_COMPLIANCE_GOVERNANCE.networkRiskAndComplianceGovernanceStatus,
    portfolioScaleGovernanceDecisionPresent:
      typeof PORTFOLIO_SCALE_GOVERNANCE_DECISION.portfolioScaleGovernanceDecision === "string",
    portfolioScaleGovernanceDecision:
      PORTFOLIO_SCALE_GOVERNANCE_DECISION.portfolioScaleGovernanceDecision,
    nextRecommendedState:
      PORTFOLIO_SCALE_GOVERNANCE_DECISION.nextRecommendedState,
  } as const
}
