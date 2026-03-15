import {
  ContextAssemblyResult,
  OrchestratorInputEnvelope,
  OrchestratorRequest,
} from "./types";

export class ContextAssembler {
  assemble(request: OrchestratorRequest): ContextAssemblyResult {
    const redactionsApplied: string[] = [];

    const assembledContext: Record<string, unknown> = {
      subject: {
        tenantId: request.subject.tenantId,
        clinicId: request.subject.clinicId ?? null,
        petId: request.subject.petId ?? null,
        consultationId: request.subject.consultationId ?? null,
        prescriptionId: request.subject.prescriptionId ?? null,
        emergencyCaseId: request.subject.emergencyCaseId ?? null,
      },
      actorRole: request.actorRole,
      taskType: request.taskType,
      input: this.redactInput(request.input, redactionsApplied),
    };

    return {
      assembledContext,
      redactionsApplied,
    };
  }

  private redactInput(
    input: OrchestratorInputEnvelope,
    redactionsApplied: string[],
  ): Record<string, unknown> {
    const result: Record<string, unknown> = {};

    if (typeof input.summary === "string") {
      result.summary = this.normalizeText(input.summary);
    }
    if (Array.isArray(input.symptoms)) {
      result.symptoms = input.symptoms.map(this.normalizeText);
    }
    if (Array.isArray(input.allergies)) {
      result.allergies = input.allergies.map(this.normalizeText);
    }
    if (Array.isArray(input.medications)) {
      result.medications = input.medications.map(this.normalizeText);
    }
    if (typeof input.weightKg === "number") {
      result.weightKg = input.weightKg;
    }
    if (typeof input.ageYears === "number") {
      result.ageYears = input.ageYears;
    }
    if (typeof input.species === "string") {
      result.species = this.normalizeText(input.species);
    }
    if (typeof input.breed === "string") {
      result.breed = this.normalizeText(input.breed);
    }
    if (typeof input.noteDraftSeed === "string") {
      result.noteDraftSeed = this.normalizeText(input.noteDraftSeed);
    }
    if (Array.isArray(input.redFlags)) {
      result.redFlags = input.redFlags.map(this.normalizeText);
    }
    if (typeof input.followupIntent === "string") {
      result.followupIntent = this.normalizeText(input.followupIntent);
    }
    if (typeof input.operationalWindow === "string") {
      result.operationalWindow = this.normalizeText(input.operationalWindow);
    }
    if (Array.isArray(input.inventorySignals)) {
      result.inventorySignals = input.inventorySignals.map(this.normalizeText);
    }

    const disallowedDirectIdentifiers = ["ownerName", "phone", "email", "nationalId"];
    for (const field of disallowedDirectIdentifiers) {
      redactionsApplied.push(field);
    }

    return result;
  }

  private normalizeText(value: string): string {
    return value.replace(/\s+/g, " ").trim();
  }
}
