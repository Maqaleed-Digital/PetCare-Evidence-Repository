PH6.2 VALIDATION MATRIX

JOURNEY J-01
NAME: Public Home
TARGET: https://myveticare.com/
EXPECTATION:
- HTTP reachable
- UI route visible
- production landing page present

JOURNEY J-02
NAME: Public Sign-in
TARGET: https://myveticare.com/signin
EXPECTATION:
- public route reachable
- no vet/admin requirement at entry

JOURNEY J-03
NAME: Public Onboarding
TARGET: https://myveticare.com/onboarding
EXPECTATION:
- public route reachable
- onboarding entry visible

JOURNEY J-04
NAME: Public Unauthorized
TARGET: https://myveticare.com/unauthorized
EXPECTATION:
- branded unauthorized page visible
- no raw forbidden JSON

JOURNEY J-05
NAME: Unauthenticated Protected Access
TARGETS:
- https://myveticare.com/vet
- https://myveticare.com/owner
- https://myveticare.com/pharmacy
- https://myveticare.com/admin
EXPECTATION:
- protected areas do not render as public
- browser journey ends in controlled unauthorized experience
- no raw JSON in normal route journey

JOURNEY J-06
NAME: Authenticated Owner Resolution
TARGET: /app or owner-safe route
EXPECTATION:
- authenticated owner resolves to owner area
- owner is not routed to vet/admin space
- owner experience remains role-safe

JOURNEY J-07
NAME: Authenticated Vet Resolution
TARGET: /app or vet route
EXPECTATION:
- authenticated vet resolves to vet area
- vet sees role-appropriate workflow surface

JOURNEY J-08
NAME: Authenticated Admin Resolution
TARGET: /app or admin route
EXPECTATION:
- authenticated admin resolves to admin area
- admin sees governance-aware operational surface

EVIDENCE REQUIREMENTS
- route header checks
- route body checks for public pages
- protected route redirect behavior
- summary file
- SHA256 manifest

STOP CONDITIONS
- raw forbidden JSON appears in standard browser journey
- protected routes become public
- public routes require vet/admin
- role-safe resolution is broken
