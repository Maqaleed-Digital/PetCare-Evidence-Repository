export interface RegulatoryAuditContract {
  auditScope: string
  auditAuthority: string
  auditEvidenceExportEnabled: boolean
  assistiveOnlyBoundaryPreserved: true
}

export const REGULATORY_AUDIT_CONTRACT: RegulatoryAuditContract = {

auditScope: "PetCare AI Clinical Assistive Runtime",

auditAuthority: "PetCare Clinical Governance Board",

auditEvidenceExportEnabled: true,

assistiveOnlyBoundaryPreserved: true

}
