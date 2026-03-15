export interface PharmacyReviewInput {
  prescriptionId: string;
  medications: string[];
  allergies: string[];
}

export interface PharmacyReviewOutput {
  workflow: "pharmacy_review";
  agent: "prescription_safety_agent";
  assistiveOnly: true;
  humanApprovalRequired: true;
  payload: {
    prescriptionId: string;
    interactionReviewRequested: boolean;
    allergyCheckRequested: boolean;
  };
}

export function buildPharmacyReviewIntegration(
  input: PharmacyReviewInput,
): PharmacyReviewOutput {
  return {
    workflow: "pharmacy_review",
    agent: "prescription_safety_agent",
    assistiveOnly: true,
    humanApprovalRequired: true,
    payload: {
      prescriptionId: input.prescriptionId,
      interactionReviewRequested: input.medications.length > 0,
      allergyCheckRequested: input.allergies.length > 0,
    },
  };
}
