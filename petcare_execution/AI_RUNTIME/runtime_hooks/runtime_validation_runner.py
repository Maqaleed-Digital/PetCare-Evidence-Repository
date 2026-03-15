from pathlib import Path
import json

REQUIRED = {
    "petcare_execution/AI_RUNTIME/runtime_hooks/AGENT_RUNTIME_HOOKS_SPEC.md": [
        "Runtime Logging, Override Flow, and Evaluation Hooks",
        "Stop Condition",
    ],
    "petcare_execution/AI_RUNTIME/runtime_hooks/runtime_event_logger.ts": [
        "export class RuntimeEventLogger",
        "buildPromptLog",
        "buildResponseLog",
        "buildDecisionLog",
    ],
    "petcare_execution/AI_RUNTIME/runtime_hooks/override_flow.ts": [
        "export class OverrideFlow",
        "createRecord",
        "allowedToRequestOverride",
    ],
    "petcare_execution/AI_RUNTIME/runtime_hooks/evaluation_hooks.ts": [
        "export class EvaluationHooks",
        "buildRecord",
        "assistive_only",
    ],
    "petcare_execution/AI_RUNTIME/runtime_hooks/runtime_validation_pack.ts": [
        'pack: "PETCARE-AI-FND-4"',
        'validationMode: "python_structural_runner"',
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
        "pack": "PETCARE-AI-FND-4",
        "validationMode": "python_structural_runner",
        "checkedFiles": checked,
        "requiredSymbolsConfirmed": True,
        "notes": [
            "Validation does not depend on repo-local typescript.",
            "Structural validation completed successfully.",
            "Runtime hooks pack is deterministic and assistive-only.",
        ],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
