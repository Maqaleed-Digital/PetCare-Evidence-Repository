import { CLINIC_RUNBOOK_READINESS } from "./clinic_runbook_readiness"
import { CONSULTATION_DAY_WORKFLOW } from "./consultation_day_workflow"
import { PHARMACY_HANDOFF_WORKFLOW } from "./pharmacy_handoff_workflow"
import { EMERGENCY_ESCALATION_WORKFLOW } from "./emergency_escalation_workflow"
import { CLINIC_SHIFT_OPEN_CLOSE_CHECKLIST } from "./clinic_shift_open_close_checklist"
import { CLINIC_RUNBOOK_CLOSURE_DECISION } from "./clinic_runbook_closure_decision"

export function buildClinicRunbookValidationPack() {
  const requiredSymbolsConfirmed =
    CLINIC_RUNBOOK_READINESS.clinicRunbookStatus === "COMPLETE" &&
    CONSULTATION_DAY_WORKFLOW.consultationWorkflowStatus === "pass" &&
    PHARMACY_HANDOFF_WORKFLOW.pharmacyHandoffWorkflowStatus === "pass" &&
    EMERGENCY_ESCALATION_WORKFLOW.emergencyEscalationWorkflowStatus === "pass" &&
    CLINIC_SHIFT_OPEN_CLOSE_CHECKLIST.shiftChecklistStatus === "pass" &&
    typeof CLINIC_RUNBOOK_CLOSURE_DECISION.closureDecision === "string"

  return {
    packId: "PETCARE-GO-LIVE-CLOSURE-2",
    requiredSymbolsConfirmed,
    clinicRunbookStatus: CLINIC_RUNBOOK_READINESS.clinicRunbookStatus,
    consultationWorkflowStatus:
      CONSULTATION_DAY_WORKFLOW.consultationWorkflowStatus,
    pharmacyHandoffWorkflowStatus:
      PHARMACY_HANDOFF_WORKFLOW.pharmacyHandoffWorkflowStatus,
    emergencyEscalationWorkflowStatus:
      EMERGENCY_ESCALATION_WORKFLOW.emergencyEscalationWorkflowStatus,
    shiftChecklistStatus:
      CLINIC_SHIFT_OPEN_CLOSE_CHECKLIST.shiftChecklistStatus,
    assistiveOnlyBoundaryPreserved:
      CLINIC_RUNBOOK_READINESS.assistiveOnlyBoundaryPreserved,
    humanApprovalStillRequired:
      CLINIC_RUNBOOK_READINESS.humanApprovalStillRequired &&
      CONSULTATION_DAY_WORKFLOW.humanApprovalStillRequired &&
      PHARMACY_HANDOFF_WORKFLOW.regulatedActionHumanControlled &&
      EMERGENCY_ESCALATION_WORKFLOW.escalationRemainsHumanDirected,
    closureDecisionPresent:
      typeof CLINIC_RUNBOOK_CLOSURE_DECISION.closureDecision === "string",
    closureDecision: CLINIC_RUNBOOK_CLOSURE_DECISION.closureDecision,
    nextRecommendedState:
      CLINIC_RUNBOOK_CLOSURE_DECISION.nextRecommendedState,
  } as const
}
