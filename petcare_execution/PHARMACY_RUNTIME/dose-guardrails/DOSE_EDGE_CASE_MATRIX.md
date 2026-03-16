DOSE EDGE CASE MATRIX

Edge-case dimensions:
- very low weight
- pediatric age
- geriatric age
- breed-specific sensitivity
- compound medication ambiguity

Requirements:
- unsupported dose context must not pass silently
- ambiguous context must require human review
- emitted result must distinguish invalid, unsupported, and review-required cases
