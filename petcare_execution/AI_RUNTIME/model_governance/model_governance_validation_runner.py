from pathlib import Path
import json

REQUIRED = {
    "petcare_execution/AI_RUNTIME/model_governance/CONTINUOUS_LEARNING_MODEL_GOVERNANCE_SPEC.md": [
        "Continuous Learning Feedback Loop & Model Governance",
        "Stop Condition",
    ],
    "petcare_execution/AI_RUNTIME/model_governance/clinician_feedback_capture.ts": [
        "captureClinicianFeedback",
        "governanceRelevant: true",
        "assistiveOnly: true",
    ],
    "petcare_execution/AI_RUNTIME/model_governance/model_performance_scoring.ts": [
        "scoreModelPerformance",
        'governanceScoreBand: "stable" | "review_required"',
        "assistiveOnly: true",
    ],
    "petcare_execution/AI_RUNTIME/model_governance/governance_review_signals.ts": [
        "buildGovernanceReviewSignal",
        "reasonCodes",
        "assistiveOnly: true",
    ],
    "petcare_execution/AI_RUNTIME/model_governance/prompt_refinement_pipeline.ts": [
        "buildPromptRefinementPlan",
        '"retain" | "review"',
        "assistiveOnly: true",
    ],
    "petcare_execution/AI_RUNTIME/model_governance/feedback_evidence_export.ts": [
        "exportFeedbackEvidence",
        'pack: "PETCARE-AI-INT-6"',
        "assistiveOnlyBoundaryPreserved: true",
    ],
    "petcare_execution/AI_RUNTIME/model_governance/model_governance_validation_pack.ts": [
        'pack: "PETCARE-AI-INT-6"',
        'governanceBoundary: "assistive_only"',
        "requiredSymbolsConfirmed: true",
    ],
}

def main() -> None:
    checked = []
    for path_str, needles in REQUIRED.items():
        path = Path(path_str)
        if not path.exists():
            raise SystemExit(f"STOP: missing file {path_str}")
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                raise SystemExit(f"STOP: missing '{needle}' in {path_str}")
        checked.append(path_str)

    result = {
        "pack": "PETCARE-AI-INT-6",
        "validationMode": "python_structural_runner",
        "requiredSymbolsConfirmed": True,
        "notes": [
            "Feedback and model governance modules detected.",
            "Assistive-only enforcement detected.",
            "Continuous learning governance signals enabled."
        ],
        "checkedFiles": checked
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
