export interface RuntimeVerificationIndexEntry {
  packId: string;
  status: "complete";
  verificationMode: "python_structural_runner" | "content_validation" | "manifest_validation";
  readinessRelevant: true;
  assistiveOnlyBoundaryPreserved: true;
}

export const RUNTIME_VERIFICATION_INDEX: RuntimeVerificationIndexEntry[] = [
  {
    packId: "PETCARE-AI-FND-1",
    status: "complete",
    verificationMode: "manifest_validation",
    readinessRelevant: true,
    assistiveOnlyBoundaryPreserved: true,
  },
  {
    packId: "PETCARE-AI-FND-2",
    status: "complete",
    verificationMode: "content_validation",
    readinessRelevant: true,
    assistiveOnlyBoundaryPreserved: true,
  },
  {
    packId: "PETCARE-AI-FND-3",
    status: "complete",
    verificationMode: "content_validation",
    readinessRelevant: true,
    assistiveOnlyBoundaryPreserved: true,
  },
  {
    packId: "PETCARE-AI-FND-4",
    status: "complete",
    verificationMode: "python_structural_runner",
    readinessRelevant: true,
    assistiveOnlyBoundaryPreserved: true,
  },
  {
    packId: "PETCARE-AI-FND-5",
    status: "complete",
    verificationMode: "python_structural_runner",
    readinessRelevant: true,
    assistiveOnlyBoundaryPreserved: true,
  },
  {
    packId: "PETCARE-AI-FND-6",
    status: "complete",
    verificationMode: "python_structural_runner",
    readinessRelevant: true,
    assistiveOnlyBoundaryPreserved: true,
  },
  {
    packId: "PETCARE-AI-FND-7",
    status: "complete",
    verificationMode: "python_structural_runner",
    readinessRelevant: true,
    assistiveOnlyBoundaryPreserved: true,
  },
  {
    packId: "PETCARE-AI-FND-8",
    status: "complete",
    verificationMode: "python_structural_runner",
    readinessRelevant: true,
    assistiveOnlyBoundaryPreserved: true,
  },
];

export class RuntimeVerificationIndex {
  list(): RuntimeVerificationIndexEntry[] {
    return RUNTIME_VERIFICATION_INDEX;
  }

  findByPackId(packId: string): RuntimeVerificationIndexEntry | undefined {
    return RUNTIME_VERIFICATION_INDEX.find((entry) => entry.packId === packId);
  }
}
