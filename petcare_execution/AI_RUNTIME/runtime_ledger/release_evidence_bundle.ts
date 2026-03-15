import {
  RUNTIME_EXECUTION_LEDGER_SAMPLE,
  RuntimeExecutionLedgerEntry,
} from "./runtime_execution_ledger";
import {
  AUDIT_CHAIN_ANCHORS,
  AuditChainAnchor,
} from "./audit_chain_anchors";

export interface LedgerSnapshotExport {
  exportType: "ledger_snapshot";
  ledgerVersion: "v1";
  entries: RuntimeExecutionLedgerEntry[];
}

export interface AuditAnchorSnapshotExport {
  exportType: "audit_anchor_snapshot";
  anchorVersion: "v1";
  anchors: AuditChainAnchor[];
}

export interface ReleaseValidationSummaryExport {
  exportType: "release_validation_summary";
  pack: "PETCARE-AI-FND-7";
  deterministic: true;
  assistiveOnlyBoundaryPreserved: true;
}

export interface ReleaseEvidenceBundle {
  ledger: LedgerSnapshotExport;
  anchors: AuditAnchorSnapshotExport;
  validation: ReleaseValidationSummaryExport;
  releaseManifestHints: string[];
  boardReadinessHints: string[];
}

export class ReleaseEvidenceBundleBuilder {
  buildBundle(): ReleaseEvidenceBundle {
    return {
      ledger: {
        exportType: "ledger_snapshot",
        ledgerVersion: "v1",
        entries: RUNTIME_EXECUTION_LEDGER_SAMPLE,
      },
      anchors: {
        exportType: "audit_anchor_snapshot",
        anchorVersion: "v1",
        anchors: AUDIT_CHAIN_ANCHORS,
      },
      validation: {
        exportType: "release_validation_summary",
        pack: "PETCARE-AI-FND-7",
        deterministic: true,
        assistiveOnlyBoundaryPreserved: true,
      },
      releaseManifestHints: [
        "include ledger snapshot digest",
        "include audit anchor snapshot digest",
        "include release validation summary digest",
      ],
      boardReadinessHints: [
        "show request-to-policy-to-prompt traceability",
        "show safety-event-linked execution posture",
      ],
    };
  }
}
