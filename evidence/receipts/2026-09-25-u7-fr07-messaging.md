# U7 · FR-07 secure chat and file sharing — AC-FR-07-01/02 closed, 2026-09-25

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.1   UNIT=U7   BASE_MAIN=b35e963ff3bb36d405416c312ca6bb7172bcf75e (U6 merged)
BRANCH=build/u7-fr07-messaging   SELECTION: FR-07 = 1 dependency criterion, ABSENT (after FR-01/FR-27 had no closable gap)
CRITERIA_CLOSED=[AC-FR-07-01, AC-FR-07-02]
GAPS_REMAINING={AC-FR-07-03: [DEPENDENCY, PERSISTENCE] — dependency PRODUCTION: production object store not bound}
FR-07: ABSENT / EVIDENCE_INCOMPLETE  ->  REACHABLE_TESTED / EVIDENCE_INCOMPLETE
```

## Build
- Migration `0040_fr07_consultation_messaging.sql` (additive): `consultation_message`, `consultation_message_attachment`
  (metadata + sha256; bytes in the document store), `notification_delivery_record` (append-only; carries the RENDERED body).
- `petcare_api/messages.py` (dataclasses, validation, tenant-checked in-memory repo) · `PostgresMessageRepository`.
- Routes (main.py): POST/GET `/api/consultations/{id}/messages`, POST `…/messages/{mid}/attachments` (reuses
  `validate_upload`: PDF/JPEG/PNG/HEIC, 15 MB), GET `…/attachments/{aid}` (served as octet-stream, nosniff).
  `_consultation_participant`: the session actor must be the consultation's owner or veterinarian in the session tenant,
  else 404. Sender from the session; every send audited (`consultation.message.sent`) and writes one IN_APP delivery
  record per other participant.
- UI `petcare_web/app/account/messages/page.tsx` (`/account/messages?consultation=<id>`): thread, send, attach, download;
  Arabic default RTL; sends no actor/owner/tenant.

## Tests
```
petcare_api/tests/test_consultation_messaging.py (served_app, 4): owner+vet exchange a message and a PNG lab report
  (byte-exact download) · invisible to a stranger owner, another vet and another tenant (404) · SVG refused ·
  delivery record with rendered body + audit, spoofed sender ignored
petcare_api/tests/test_consultation_messaging_postgres.py (2): second-instance read-back; empty message / orphan
  attachment refused
petcare_web/__tests__/fr07-messages.test.tsx (vitest, 2): Arabic RTL thread with download link; send + upload with no
  actor/tenant in the body (5/5 consecutive passes after hardening waits for a loaded machine)
PERTURBATIONS
  P-AC01 participant check removed      -> test_messages_are_invisible_outside_the_consultation FAILS            ARMED
  P-AC02 delivery record not written    -> test_each_delivery_attempt_is_recorded_with_the_rendered_body… FAILS ARMED
```

## Binding and evidence
- bindings FR-07 (was ABSENT): 8 implements, 4 routes, 2 test files; fitness PERSISTENT_POSTGRES / SESSION / SESSION,
  ui_surface [/account/messages]; `unresolved` records the AC-03 production gap and the in-memory consultation store.
- evidence.json: AC-FR-07-01 {SERVED_APP_E2E, TENANT_ISOLATION: TEST · UI, ARABIC_RTL: ARTEFACT} ·
  AC-FR-07-02 {PERSISTENCE, AUDIT: TEST}. served_routes 43 → 47.

## Results
```
REGRESSION_LOCAL(python)=1022 passed / 0 skipped · M4: no FR lowered; ACCEPTED=[FR-02] · TSC clean
WEB_UNIT(local): 10 failures under load average 135 (5 s test timeout); the failing files are byte-identical to
  origin/main and all 32 of their tests pass with --testTimeout=60000 — environmental, not a regression. CI is the
  authoritative run (M1).
SCANNERS: SECRET_SCAN=CLEAN · ACTIVE_LITERAL_DEFAULT=0 · DIFF_CHECK=CLEAN
```

## Findings
- **AC-FR-07-02 encryption.** The statement names NFR-05 encryption at rest/in transit; its ratified evidence types are
  PERSISTENCE and AUDIT only. Encryption is evidenced under NFR-05 (environment PRODUCTION), not here.
- **Consultation sessions are in-memory.** Messages are durable, but the consultation they reference is still a
  module-level dict (pre-existing; FR-06 domain). A restart loses the participant lookup for existing consultations.
