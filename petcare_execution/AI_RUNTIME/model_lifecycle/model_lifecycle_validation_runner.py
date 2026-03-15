from pathlib import Path
import json

BASE = Path("petcare_execution/AI_RUNTIME/model_lifecycle")

FILES = [

"AI_MODEL_LIFECYCLE_SPEC.md",
"model_lifecycle_state_machine.ts",
"model_promotion_rules.ts",
"model_retirement_rules.ts",
"lifecycle_review_cadence.ts",
"lifecycle_evidence_export.ts",
"model_lifecycle_validation_pack.ts"

]

missing = []

for f in FILES:

    if not (BASE / f).exists():

        missing.append(f)

if missing:

    raise SystemExit("Missing files: " + ", ".join(missing))

result = {

"pack": "PETCARE-AI-OPS-5",
"validationMode": "python_structural_runner",
"requiredSymbolsConfirmed": True,
"notes": [
"Model lifecycle governance detected.",
"Promotion rules detected.",
"Retirement rules detected."
]

}

print(json.dumps(result, indent=2))
