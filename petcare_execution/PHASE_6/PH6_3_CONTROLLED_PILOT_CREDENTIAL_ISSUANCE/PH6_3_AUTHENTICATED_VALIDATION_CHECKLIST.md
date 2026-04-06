PH6.3 AUTHENTICATED ROLE JOURNEY VALIDATION CHECKLIST

JOURNEY A-01
ROLE: OWNER
STEPS
- issue controlled owner credential
- complete first sign-in
- verify owner lands in owner-safe route
- verify owner does not enter vet/admin space
- record outcome

EXPECTED RESULT
- authenticated owner resolves correctly
- no wrong-role access
- no raw forbidden JSON in standard browser journey

JOURNEY A-02
ROLE: VET
STEPS
- issue controlled vet credential
- complete first sign-in
- verify vet lands in vet-safe route
- verify vet sees role-appropriate surface
- record outcome

EXPECTED RESULT
- authenticated vet resolves correctly
- no wrong-role access
- protected routing preserved

JOURNEY A-03
ROLE: ADMIN
STEPS
- issue controlled admin credential
- complete first sign-in
- verify admin lands in admin-safe route
- verify admin sees governance-aware surface
- record outcome

EXPECTED RESULT
- authenticated admin resolves correctly
- no wrong-role access
- protected routing preserved

MANDATORY EVIDENCE
- issuance record completed
- browser outcome recorded
- route result recorded
- role-safe resolution recorded
- notes on any mismatch

STOP CONDITIONS
- wrong area resolution
- missing issuance trace
- prototype/demo account used as pilot proof
- shared credential used
