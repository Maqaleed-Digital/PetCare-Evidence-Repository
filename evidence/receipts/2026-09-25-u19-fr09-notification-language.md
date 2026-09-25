# U19 · FR-09 AC-FR-09-03 — notifications and documents in the recipient's language; FR-09 ACCEPTED, 2026-09-25

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.1   UNIT=U19   BASE_MAIN=99509efa7b15507d3725c400e7858eb105eb0a76 (U18 merged, PR #63)
BRANCH=build/u19-fr09-ac03
SELECTION (pass 2): gaps with dependency NONE remain on FR-09 (0 dependency criteria), FR-01 (1) and FR-06 (2);
  FR-09 first by the rule.
CRITERIA_CLOSED=[AC-FR-09-03]
GAPS_REMAINING={}
FR-09: REACHABLE_TESTED / EVIDENCE_INCOMPLETE  ->  REACHABLE_TESTED / ACCEPTED (checker v1.3)
```

## Defect found and fixed
Two of the four notification/document paths rendered English only — AC-FR-09-03's fails_if ("an Arabic-preferring
owner receives a notification or document only in English"):
- FR-07 consultation-message notifications (`_render_notification`) — now rendered per RECIPIENT;
- FR-19 recall notices — now `recalls.render_notice(language, …)` per owner.
FR-20 receipts and FR-23 reminders already followed the owner's language. `_recipient_language(user_id)` = the
recipient's stored preference, Arabic (primary) by default.

## Evidence
AC-03 {SERVED_APP_E2E `test_fr09_notification_language.py` — one Arabic-preferring and one English-preferring owner drive
all four paths through the served app; every Arabic owner text carries Arabic script, no English owner text does ·
ARABIC_RTL: the existing, unchanged artefacts `fr20-cod-orders.test.tsx` (Arabic receipt rendered RTL) and
`fr23-reminders.test.tsx` (Arabic reminders RTL)}. FR-09 is ACCEPTED by checker v1.3 — the second ACCEPTED FR.

## Perturbations
```
P-AC03-MESSAGE-ENGLISH    message notification always English       -> AC-03 test FAILS   ARMED
P-AC03-RECALL-ENGLISH     recall notice always English              -> AC-03 test FAILS   ARMED
P-AC03-SENDER-LANGUAGE    recipient preference ignored (default)    -> AC-03 test FAILS   ARMED
PERTURBATIONS=3 ARMED=3 VACUOUS=0
```
