PETCARE PHASE 2 DF-01
Emergent Prompt

Repository:
"/Users/waheebmahmoud/dev/petcare-evidence-repository"

Objective:
Execute GCP foundation setup for PetCare.

Required outputs:
- PHASE2_DF01_EXECUTION_SPEC.md
- phase2_df01_gcp_foundation.sh
- PHASE2_DF01_IAM_BASELINE.md
- PHASE2_DF01_NETWORK_BASELINE.md
- PHASE2_DF01_SECURITY_BASELINE.md
- PHASE2_DF01_NOTION_UPDATE.md
- PHASE2_DF01_EMERGENT_PROMPT.md
- evidence pack

Rules:
- full files only
- overwrite-safe writes only
- commit and push once
- no sandbox to production routing
- no shared credentials across environments
- no shared networks across prod and sandbox
- no hidden project creation
- capture outputs to evidence

Stop condition:
Stop only if organization permissions, billing permissions, or folder access block foundation provisioning.
If that occurs, emit STOP_REPORT.md and stop.
