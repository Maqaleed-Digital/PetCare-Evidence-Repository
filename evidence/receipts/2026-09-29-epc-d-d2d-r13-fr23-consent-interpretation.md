# MVC-EPC-D-001 v1.5 — D2d: Sponsor ruling R13 (2026-09-29) — FR-23 consent interpretation, recorded as a receipt

Recorded here, not under governance/**: instrument v1.5 LIMITS forbid any change to governance/** and requirements/**
("new receipts only"). The ratified AC-FR-23-01 text in requirements/acceptance/phase1_high_pack.ratified.json is
unchanged; this receipt records the governed interpretation R13.2 attaches to it.

```
ACT_ID=MVC-EPC-D-001-R13-FR23-CONSENT
STATUS=RATIFIED
DATE=2026-09-29
LOCK=YES
DECISION=OPTION_A

R10 (authoritative): care_reminders dispatch is fail-closed. Absent, revoked, false, expired where applicable,
malformed, unreadable or otherwise indeterminate effective consent MUST prevent dispatch.
This is a governed product/security decision. It is NOT a legal conclusion about the lawful basis for care
reminders under Saudi PDPL. No engineering evidence may represent it as such.

AC-FR-23-01 INTERPRETATION (ratified text unchanged):
"Defaults apply to every consenting owner and may not be suppressed by tenant or user configuration.
An owner's own care_reminders consent grant, absence, or withdrawal is not tenant/user reminder configuration.
This engineering interpretation does not determine the statutory lawful basis under PDPL and makes no
legal-compliance claim."

R13.1 EVIDENCE: the four affected registered tests change ONLY their precondition — each test owner first grants
care_reminders through the governed consent route (POST /api/me/consents/care_reminders) before the reminder run.
Substantive assertions are byte-identical (insert-only diffs). Test node ids, and therefore acceptance counts, are
unchanged.

No counsel dependency is created for D2d. A later legal determination requiring a different lawful-basis model is
handled by a separate explicit governance ruling.
```
