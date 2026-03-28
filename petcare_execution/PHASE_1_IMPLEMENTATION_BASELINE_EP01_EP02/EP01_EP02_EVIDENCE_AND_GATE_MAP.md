# EP-01 EP-02 EVIDENCE AND GATE MAP

Pack ID: PETCARE-EP01-EP02-IMPLEMENTATION-BASELINE

## 1. Gate mapping

### EP-01
- G-S1 Security Gate
- G-R1 Regulatory and Privacy Gate

### EP-02
- G-C1 Clinical Safety Gate
- G-S1 Security Gate
- G-A1 AI Governance Gate

## 2. Minimum evidence required for next build wave

### EP-01 evidence
- role matrix implementation trace
- consent model implementation trace
- access denial behavior trace
- audit event sample list
- permission test plan

### EP-02 evidence
- schema implementation trace
- timeline read model trace
- CRUD audit trace
- document access policy trace
- AI redaction test plan
- protected data handling notes

## 3. Minimum validation expectations for next build wave

- unauthorized access path returns forbidden
- consent create and revoke flows are testable
- audit events generated on protected actions
- UPHR entity mutations record actor and timestamp
- document access is controlled
- AI prompt-safe redaction happens before AI usage

## 4. Done rule

No EP-01 or EP-02 hard-gated story may move to done unless the relevant evidence link is attached.
