export interface EvidenceManifestChainEntry {
  chainOrder: number;
  packId: string;
  baselineCommit: string;
  evidencePathHint: string;
  readinessRelevant: true;
}

export const EVIDENCE_MANIFEST_CHAIN: EvidenceManifestChainEntry[] = [
  {
    chainOrder: 1,
    packId: "PETCARE-AI-FND-1",
    baselineCommit: "22a7d54be77a46505af335502643bd848cbf98d4",
    evidencePathHint: "petcare_execution/EVIDENCE/PETCARE-AI-FND-1",
    readinessRelevant: true,
  },
  {
    chainOrder: 2,
    packId: "PETCARE-AI-FND-2",
    baselineCommit: "22a7d54be77a46505af335502643bd848cbf98d4",
    evidencePathHint: "petcare_execution/EVIDENCE/PETCARE-AI-FND-2",
    readinessRelevant: true,
  },
  {
    chainOrder: 3,
    packId: "PETCARE-AI-FND-3",
    baselineCommit: "7ed02ca8db03b3d23a5dc1406eb88873a36ae484",
    evidencePathHint: "petcare_execution/EVIDENCE/PETCARE-AI-FND-3",
    readinessRelevant: true,
  },
  {
    chainOrder: 4,
    packId: "PETCARE-AI-FND-4",
    baselineCommit: "810e2622d22b6b61f14040de6a109f7ffee18759",
    evidencePathHint: "petcare_execution/EVIDENCE/PETCARE-AI-FND-4",
    readinessRelevant: true,
  },
  {
    chainOrder: 5,
    packId: "PETCARE-AI-FND-5",
    baselineCommit: "7479c497bf1dad84623263f561c939006519039d",
    evidencePathHint: "petcare_execution/EVIDENCE/PETCARE-AI-FND-5",
    readinessRelevant: true,
  },
  {
    chainOrder: 6,
    packId: "PETCARE-AI-FND-6",
    baselineCommit: "bfa03859364b031a3d8c21f6dd065cd78ceeddf6",
    evidencePathHint: "petcare_execution/EVIDENCE/PETCARE-AI-FND-6",
    readinessRelevant: true,
  },
  {
    chainOrder: 7,
    packId: "PETCARE-AI-FND-7",
    baselineCommit: "8f3562dced05e18f5e235297a4ff6d2a84e78f19",
    evidencePathHint: "petcare_execution/EVIDENCE/PETCARE-AI-FND-7",
    readinessRelevant: true,
  },
  {
    chainOrder: 8,
    packId: "PETCARE-AI-FND-8",
    baselineCommit: "570a9999a382b1b6e693aebf2f78c720a0762014",
    evidencePathHint: "petcare_execution/EVIDENCE/PETCARE-AI-FND-8",
    readinessRelevant: true,
  },
];

export class EvidenceManifestChain {
  list(): EvidenceManifestChainEntry[] {
    return EVIDENCE_MANIFEST_CHAIN;
  }

  findByPackId(packId: string): EvidenceManifestChainEntry | undefined {
    return EVIDENCE_MANIFEST_CHAIN.find((entry) => entry.packId === packId);
  }
}
