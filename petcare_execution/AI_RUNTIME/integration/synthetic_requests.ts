/**
 * STATUS=STALE_DESIGN_ARTEFACT
 * SUPERSEDED_BY=W0-D
 * PHARMACY_OPERATOR_DISPENSING=RETIRED
 * DO_NOT_IMPLEMENT_FROM_THIS_FILE
 *
 * W0-D retires `pharmacy_operator` and fails dispensing closed to the
 * veterinarian. This file predates that decision and still models the role as a
 * first-class authorization concept. It is retained as a design record of what
 * was once intended, not as a specification to build from.
 *
 * It grants no authority. Nothing under petcare_execution/ is compiled,
 * type-checked or executed — there is no tsconfig.json or package.json anywhere
 * in this tree — so this file has no runtime effect. Deleting it would destroy
 * the record of a superseded decision; implementing from it would reverse a
 * security decision. Marked, retained, and registered in
 * GOVERNANCE/CANONICAL_REPOSITORY_AUTHORITY/RETIRED_ROLE_CUSTODY_REGISTER.json.
 */
import { OrchestratorRequest } from "../orchestrator/types";

export const SYNTHETIC_REQUESTS: OrchestratorRequest[] = [
  {
    requestId: "req_history_001",
    actorRole: "veterinarian",
    taskType: "summarize_history",
    subject: {
      tenantId: "tenant_petcare",
      clinicId: "clinic_jeddah_01",
      petId: "pet_001",
      consultationId: "consult_001",
    },
    input: {
      summary: "Recurring skin irritation and prior food allergy episodes.",
      symptoms: ["itching", "skin redness"],
      allergies: ["chicken protein"],
      medications: ["antihistamine"],
      ageYears: 4,
      species: "canine",
      breed: "labrador",
    },
  },
  {
    requestId: "req_note_001",
    actorRole: "veterinarian",
    taskType: "draft_consult_note",
    subject: {
      tenantId: "tenant_petcare",
      clinicId: "clinic_jeddah_01",
      petId: "pet_002",
      consultationId: "consult_002",
    },
    input: {
      summary: "Follow-up consultation for post-treatment recovery.",
      symptoms: ["reduced appetite"],
      noteDraftSeed: "Recovery appears stable but needs review.",
      ageYears: 7,
      species: "feline",
      breed: "persian",
    },
  },
  {
    requestId: "req_med_001",
    actorRole: "pharmacy_operator",
    taskType: "medication_safety_review",
    subject: {
      tenantId: "tenant_petcare",
      clinicId: "clinic_jeddah_01",
      petId: "pet_003",
      prescriptionId: "rx_001",
    },
    input: {
      medications: ["drug_a", "drug_b"],
      allergies: ["penicillin"],
      weightKg: 8,
      ageYears: 3,
      species: "canine",
      breed: "beagle",
    },
  },
  {
    requestId: "req_emergency_001",
    actorRole: "veterinarian",
    taskType: "emergency_intake_support",
    subject: {
      tenantId: "tenant_petcare",
      clinicId: "clinic_jeddah_01",
      petId: "pet_004",
      emergencyCaseId: "er_001",
    },
    input: {
      symptoms: ["rapid breathing", "collapse"],
      redFlags: ["respiratory distress"],
      species: "feline",
      breed: "mixed",
    },
  },
  {
    requestId: "req_ops_001",
    actorRole: "platform_admin",
    taskType: "operations_forecast",
    subject: {
      tenantId: "tenant_petcare",
      clinicId: "clinic_jeddah_01",
    },
    input: {
      operationalWindow: "next_14_days",
      inventorySignals: ["high vaccine demand", "low anti-inflammatory stock"],
    },
  },
  {
    requestId: "req_followup_001",
    actorRole: "partner_admin",
    taskType: "client_followup_draft",
    subject: {
      tenantId: "tenant_petcare",
      clinicId: "clinic_jeddah_01",
      petId: "pet_005",
      consultationId: "consult_005",
    },
    input: {
      followupIntent: "appointment reminder and medication adherence check-in",
      summary: "Routine follow-up communication.",
    },
  },
];
