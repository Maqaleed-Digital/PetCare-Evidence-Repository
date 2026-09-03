# G-C1 Pharmacy — Safety Engine Rules

## File: `app/backend/services/medication_safety.py`

## Interaction table (18 pairs seeded)

| Pair | Severity | Notes |
|------|----------|-------|
| med 1 + med 2 | **contraindicated** | NSAIDs + corticosteroids: GI bleeding |
| med 3 + med 4 | **contraindicated** | Metronidazole + warfarin |
| med 1 + med 5 | major | Aspirin + furosemide |
| med 2 + med 6 | major | Prednisolone + cyclosporine |
| med 3 + med 7 | major | Metronidazole + phenobarbital |
| med 8 + med 9 | major | Doxycycline + antacids |
| med 1 + med 10 | moderate | Aspirin + enrofloxacin |
| med 4 + med 11 | moderate | Warfarin + vitamin K |
| med 5 + med 12 | moderate | Furosemide + digoxin |
| med 6 + med 13 | moderate | Cyclosporine + ketoconazole |
| med 14 + med 15 | moderate | Tramadol + serotonergic drugs |
| med 1 + med 16 | minor | Aspirin + iron |
| med 17 + med 18 | minor | Amoxicillin + tetracycline |

## Blocking logic

- `contraindicated` or `major` → **BLOCK** (HTTP 403 unless override_reason provided)
- `moderate` or `minor` → warn only
- Allergy match (any ingredient overlap) → **BLOCK**
- Dose out of range → warn only (non-blocking)

## Override

Override of a blocking alert requires:
- `override_reason` field in dispense request (non-empty)
- Emits `pharmacy.safety_override` audit event with reason

## Allergy check

`check_allergies(db, pet_id, medication_id)` — compares `Pet.allergies` list
against `Medication.ingredients` list. Any overlap → alert=True, blocks dispense.

## Dose guardrails

`check_dose_guardrails(med_id, species, weight_kg, age_months, dose)` — looks up
`DOSE_REFERENCE[(med_id, species)]` for min/max/recommended mg/kg values.
Out-of-range → warning in SafetyReport, does not block.
