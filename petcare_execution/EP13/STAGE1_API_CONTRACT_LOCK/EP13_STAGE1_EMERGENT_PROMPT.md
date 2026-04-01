# EP-13 Stage 1 — Emergent Execution Prompt

You are executing inside the PetCare repository only.

Repository root:
"/Users/waheebmahmoud/dev/petcare-evidence-repository"

Authoritative source-of-truth commit before this work:
"b702f08f4b14c23a882b4bd9eac4bf397c390bd8"

Objective:
Create the EP-13 Stage 1 API contract lock pack for external platform exposure.

Required outputs:
1. "petcare_execution/EP13/STAGE1_API_CONTRACT_LOCK/EP13_STAGE1_API_CONTRACT_SPEC.md"
2. "petcare_execution/EP13/STAGE1_API_CONTRACT_LOCK/EP13_STAGE1_OPENAPI.yaml"
3. "petcare_execution/EP13/STAGE1_API_CONTRACT_LOCK/EP13_STAGE1_NOTION_UPDATE.md"
4. "petcare_execution/EP13/STAGE1_API_CONTRACT_LOCK/EP13_STAGE1_EMERGENT_PROMPT.md"
5. Evidence pack under:
   "petcare_execution/EVIDENCE/PETCARE-PHASE-1-BUILD-EP13-STAGE1-API-CONTRACT-LOCK/<UTC_RUN>/"

Non-negotiable rules:
- Do not change EP-08 through EP-12 governance semantics
- Do not introduce external execution authority
- Do not expose payment execution
- Do not expose approval bypass capability
- Do not expose treasury mutation capability
- Do not invent additional business domains
- Do not alter prior locked architecture intent
- Use overwrite-safe writes only
- Full files only
- Deterministic manifest required
- Commit and push once complete

Stage 1 contract must lock:
- endpoint inventory
- read versus controlled write boundary
- request and response schemas
- required headers
- auth scopes
- webhook event envelope
- signature rules
- error envelope
- rate limiting headers
- traceability chain

Controlled write rule:
Every external write endpoint must create an internal governed request only.
No direct execution path allowed.

Required endpoint families:
- /v1/partner/profile
- /v1/orders
- /v1/orders/{order_id}
- /v1/referrals
- /v1/referrals/{referral_id}
- /v1/availability
- /v1/catalog/batches
- /v1/catalog/batches/{catalog_batch_id}
- /v1/webhook-subscriptions
- /v1/webhook-subscriptions/{subscription_id}/pause
- /v1/webhook-subscriptions/{subscription_id}/resume
- /v1/webhook-subscriptions/{subscription_id}
- /v1/events/{event_id}

Required evidence outputs:
- file_listing.txt
- sha256.txt
- MANIFEST.json
- git_head.txt
- git_status.txt

Stop condition:
Stage 1 is complete when all artifacts are written, evidence pack is sealed, and commit is pushed.
