import { RUNTIME_POLICY_BUNDLES, RuntimePolicyBundle } from "./runtime_policy_bundles";
import { PROMPT_REGISTRY_BINDINGS, PromptRegistryBinding } from "./prompt_registry_binding";

export interface PolicyBundleSnapshotExport {
  exportType: "policy_bundle_snapshot";
  policyVersion: "v1";
  bundles: RuntimePolicyBundle[];
}

export interface PromptBindingSnapshotExport {
  exportType: "prompt_binding_snapshot";
  promptBindingVersion: "v1";
  bindings: PromptRegistryBinding[];
}

export interface AuditValidationSummaryExport {
  exportType: "audit_validation_summary";
  pack: "PETCARE-AI-FND-6";
  deterministic: true;
  assistiveOnlyBoundaryPreserved: true;
}

export interface AuditBundleExport {
  policyBundles: PolicyBundleSnapshotExport;
  promptBindings: PromptBindingSnapshotExport;
  registryLinkageHints: string[];
  safetyTaxonomyLinkageHints: string[];
  validation: AuditValidationSummaryExport;
  exportManifestHints: string[];
}

export class AuditBundleExportBuilder {
  buildBundle(): AuditBundleExport {
    return {
      policyBundles: {
        exportType: "policy_bundle_snapshot",
        policyVersion: "v1",
        bundles: RUNTIME_POLICY_BUNDLES,
      },
      promptBindings: {
        exportType: "prompt_binding_snapshot",
        promptBindingVersion: "v1",
        bindings: PROMPT_REGISTRY_BINDINGS,
      },
      registryLinkageHints: [
        "link policy bundle by task family",
        "link prompt binding by policy bundle id",
      ],
      safetyTaxonomyLinkageHints: [
        "map blocked action classes to safety event taxonomy",
        "map reviewer requirements to review-required safety events",
      ],
      validation: {
        exportType: "audit_validation_summary",
        pack: "PETCARE-AI-FND-6",
        deterministic: true,
        assistiveOnlyBoundaryPreserved: true,
      },
      exportManifestHints: [
        "include policy bundle snapshot digest",
        "include prompt binding snapshot digest",
        "include validation summary digest",
      ],
    };
  }
}
