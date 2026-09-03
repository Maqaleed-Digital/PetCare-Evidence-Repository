# Production remediation plan — AUTHORED, NOT APPLIED

**NO STEP BELOW HAS BEEN EXECUTED.** Every one is Sponsor-gated. The ordering matters:
IR-01 and IR-02 are read-only and must precede everything, because the mutations
destroy the evidence that classifies the incident.

| # | Action | Production mutation | Gate class | Rollback | Evidence required | Acceptance |
|---|---|---|---|---|---|---|
| **IR-01** | Preserve cloud + log evidence: run `GCP_FORENSIC_READ_CARD.md` steps 0–9, capture to a hashed bundle | **NO** | none (read-only) | n/a | command transcripts + SHA-256 | all 9 steps produce output or a recorded failure |
| **IR-02** | Establish current deployed revision + image digest (card steps 2–4) | **NO** | none | n/a | revision list with creation timestamps | `CURRENT_DEPLOYED_REVISION` and `..._IMAGE` are concrete values, not UNKNOWN |
| **IR-02b** | **Decide from IR-01/02 whether an incident exists at all.** If no revision post-dates 2026-05-23, close as NO-INCIDENT and stop | **NO** | none | n/a | determination doc | a written YES/NO on `VULNERABLE_IMAGE_EXECUTED` |
| **IR-03** | Generate a new signing key from a CSPRNG (≥32 bytes) | NO (local) | `GATE_CREDENTIAL_ENTRY` | discard | key **never** printed to transcript | length + source attested, value unlogged |
| **IR-04** | Write the new key to governed secret storage (AWS Secrets Manager / SSM per the AWS decision) | **YES** | `GATE_CREDENTIAL_ENTRY` | restore prior version | secret version id only | version id returned; value not echoed |
| **IR-05** | Deploy the W0-A-fixed runtime with `SECRET_KEY` sourced from IR-04 | **YES** | `GATE_LIVE_APPLY` | redeploy prior revision | build id, image digest, revision name | service returns 200 on `/health` from application code, not Google Frontend |
| **IR-06** | Invalidate sessions issued under the old key | **subsumed by IR-04** | — | — | — | **Automatic.** Single-key design with no previous-key list ⇒ rotation invalidates every prior cookie. No separate purge exists or is needed (see `SESSION_RISK_MODEL.md`) |
| **IR-07** | Verify the invoker policy is *intentional* — decide public vs authenticated and set it deliberately | **YES** | `GATE_LIVE_APPLY` | reapply prior IAM policy | before/after `get-iam-policy` | policy matches a written decision, not an inherited default |
| **IR-08** | Verify the old key is no longer accepted | **NO** | none | n/a | probe transcript | a cookie signed with the retired literal is rejected |
| **IR-09** | Audit retained auth/session logs across the window | **NO** | none | n/a | log query output | either evidence of issuance, or a recorded retention gap |
| **IR-10** | Post-incident security acceptance + register update | NO | none | n/a | signed determination | classification moved off `INDETERMINATE` |

## Two notes on sequencing

**IR-02b is the real decision point.** On current evidence the chain that would make
this an incident is broken — the only documented deployment predates the vulnerable
code by seven weeks. IR-01/IR-02 are cheap, read-only, and may close the whole thing.
Rotating and redeploying before reading is spending a production mutation to answer a
question a read would have answered.

**IR-07 is separable and is worth doing regardless.** Whether or not the vulnerable
code ever ran, a service object that answers anonymous callers without an IAM denial
should have its invoker policy set by decision rather than inheritance.
