# G-C1 — Escalation Engine Rules

## File: `app/backend/services/escalation_engine.py`

## RED_FLAG_RULES

```python
RED_FLAG_RULES = {
    "dog": [
        "breathing_difficulty",
        "seizure",
        "collapse",
        "severe_bleeding",
        "suspected_poisoning",
        "eye_injury",
        "difficulty_urinating",
    ],
    "cat": [
        "open_mouth_breathing",
        "urinary_blockage",
        "prolonged_seizure",
        "suspected_toxin",
        "severe_lethargy",
        "rapid_weight_loss",
    ],
    "bird": [
        "laboured_breathing",
        "fluffed_feathers_unresponsive",
        "bleeding",
    ],
    "all": [
        "loss_of_consciousness",
        "suspected_trauma",
        "extreme_pain",
    ],
}
```

## SEVERITY_MAP

| Symptom | Severity |
|---------|----------|
| breathing_difficulty | critical |
| open_mouth_breathing | critical |
| urinary_blockage | critical |
| seizure | critical |
| collapse | critical |
| suspected_poisoning | critical |
| loss_of_consciousness | critical |
| severe_bleeding | critical |
| extreme_pain | critical |
| prolonged_seizure | urgent |
| suspected_toxin | urgent |
| severe_lethargy | urgent |
| rapid_weight_loss | urgent |
| difficulty_urinating | urgent |
| eye_injury | urgent |
| laboured_breathing | urgent |
| fluffed_feathers_unresponsive | urgent |
| bleeding | urgent |
| suspected_trauma | urgent |

## Escalation logic

1. Merge species-specific rules + `all` rules.
2. Find intersection with submitted symptoms.
3. If any match is `critical` → `severity=critical`, `recommended_action=emergency_vet`.
4. If matches exist but none critical → `severity=urgent`, `recommended_action=urgent_consult`.
5. No matches → `severity=routine`, `recommended_action=standard_consult`.

## Contract

`evaluate_escalation(species: str, symptoms: list[str]) -> dict`

Pure function — no DB access, no side effects. Callers must log the result.
