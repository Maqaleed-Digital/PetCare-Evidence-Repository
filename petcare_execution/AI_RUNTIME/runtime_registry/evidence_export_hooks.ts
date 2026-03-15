import { RuntimeRegistryEntry, RUNTIME_REGISTRY } from "./runtime_registry";
import { SafetyEventDefinition, SAFETY_EVENT_TAXONOMY } from "./safety_event_taxonomy";

export interface RegistrySnapshotExport {
  exportType: "registry_snapshot";
  registryVersion: "v1";
  entries: RuntimeRegistryEntry[];
}

export interface SafetyEventBundleExport {
  exportType: "safety_event_bundle";
  taxonomyVersion: "v1";
  events: SafetyEventDefinition[];
}

export interface ValidationSummaryExport {
  exportType: "validation_summary";
  pack: "PETCARE-AI-FND-5";
  deterministic: true;
  assistiveOnlyBoundaryPreserved: true;
}

export interface EvidenceExportBundle {
  registry: RegistrySnapshotExport;
  safetyEvents: SafetyEventBundleExport;
  validation: ValidationSummaryExport;
  exportManifestHints: string[];
}

export class EvidenceExportHooks {
  buildBundle(): EvidenceExportBundle {
    return {
      registry: {
        exportType: "registry_snapshot",
        registryVersion: "v1",
        entries: RUNTIME_REGISTRY,
      },
      safetyEvents: {
        exportType: "safety_event_bundle",
        taxonomyVersion: "v1",
        events: SAFETY_EVENT_TAXONOMY,
      },
      validation: {
        exportType: "validation_summary",
        pack: "PETCARE-AI-FND-5",
        deterministic: true,
        assistiveOnlyBoundaryPreserved: true,
      },
      exportManifestHints: [
        "include registry snapshot digest",
        "include safety taxonomy digest",
        "include validation summary digest",
      ],
    };
  }
}
