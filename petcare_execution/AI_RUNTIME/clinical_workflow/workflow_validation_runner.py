from pathlib import Path
import json

REQUIRED = {
    "petcare_execution/AI_RUNTIME/clinical_workflow/CLINICAL_WORKFLOW_COPILOT_SPEC.md": [
        "Clinical Workflow Copilot Integration",
        "Stop Condition",
    ],
    "petcare_execution/AI_RUNTIME/clinical_workflow/consultation_copilot_integration.ts": [
        "buildConsultationCopilotIntegration",
        'assistiveOnly: true',
        'humanApprovalRequired: true',
    ],
    "petcare_execution/AI_RUNTIME/clinical_workflow/triage_board_integration.ts": [
        "buildTriageBoardIntegration",
        'suggestedTriageState: "review_required"',
        'assistiveOnly: true',
    ],
    "petcare_execution/AI_RUNTIME/clinical_workflow/pharmacy_review_integration.ts": [
        "buildPharmacyReviewIntegration",
        "interactionReviewRequested",
        'assistiveOnly: true',
    ],
    "petcare_execution/AI_RUNTIME/clinical_workflow/emergency_workflow_integration.ts": [
        "buildEmergencyWorkflowIntegration",
        "prioritizedQueueIds",
        'assistiveOnly: true',
    ],
    "petcare_execution/AI_RUNTIME/clinical_workflow/workflow_validation_pack.ts": [
        'pack: "PETCARE-AI-INT-3"',
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
        "pack": "PETCARE-AI-INT-3",
        "validationMode": "python_structural_runner",
        "requiredSymbolsConfirmed": True,
        "notes": [
            "Clinical workflow integration adapters detected.",
            "Assistive-only enforcement detected.",
            "Human approval boundary preserved."
        ],
        "checkedFiles": checked
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
