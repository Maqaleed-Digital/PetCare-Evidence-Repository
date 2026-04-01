EP-14 DEPENDENCY MAP

Depends on EP-13:
- endpoint registry
- auth scope matrix
- integration gateway scaffold
- webhook model
- audit & trace model

Depends on EP-10:
- operational control layer
- integration governance

Depends on EP-11:
- execution boundary enforcement

Depends on EP-12:
- advisory AI (for partner monitoring only)

New Components Introduced:
- sandbox isolation layer
- partner credential registry
- onboarding workflow state machine
- simulation engine
- webhook replay engine

Constraints:
- no bypass of EP-11 execution gates
- no write mutation beyond request-intake
- sandbox must never impact production data
