# EP-02 UI SURFACE MAPPING

Pack ID: PETCARE-EP01-EP02-IMPLEMENTATION-BASELINE

## 1. Surfaces in scope

### Owner
- Pet profile view and update
- Health timeline view
- Consent management view
- Document visibility view

### Veterinarian
- Pet profile view
- Medical timeline view
- Add allergy record
- Add medication record
- Add vaccination record
- Add lab result
- Add clinical note

### Pharmacy Operator
- Medication-relevant limited record visibility only where later workflow authorizes it
- No unrestricted full-UPHR browsing surface in EP-02

### Partner Clinic Admin
- No direct clinical record editing surface in EP-02

### Platform Admin
- Audit and governance-only visibility remains purpose-limited and not a replacement for clinical workflow

## 2. Route baseline

Suggested PHASE 1 route baseline for later implementation:
- /owner/pets
- /owner/pets/{pet_id}
- /owner/pets/{pet_id}/timeline
- /owner/pets/{pet_id}/consent
- /vet/pets/{pet_id}
- /vet/pets/{pet_id}/timeline
- /vet/pets/{pet_id}/notes/new
- /vet/pets/{pet_id}/allergies/new
- /vet/pets/{pet_id}/medications/new
- /vet/pets/{pet_id}/vaccinations/new
- /vet/pets/{pet_id}/labs/new
- /admin/audit

## 3. UI rules

- owner sees owner-scoped actions only
- vet sees care-scoped actions only
- deny-by-default for unauthorized actions
- document visibility obeys consent and access policy
- timeline must clearly separate categories
- AI usage of UPHR data must rely on redacted prompt-safe views only

## 4. Non-goals for this pack

This pack does not define:
- Tele-Vet consultation UI
- Pharmacy operational queue UI
- Emergency network UI
- Marketplace admin UI
