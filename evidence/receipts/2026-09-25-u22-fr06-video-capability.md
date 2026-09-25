# U22 · FR-06 video consultation capability, built behind the REG-02 gate (not registered — SQ-2), 2026-09-25

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.1   UNIT=U22   BASE_MAIN=a3c3bbdeeb41bc947b6711abfbe2bd696627242e (U21 merged, PR #66)
BRANCH=build/u22-fr06-video
SELECTION (pass 2): FR-06 AC-01/02 — the last gaps with dependency NONE that carry internally buildable work
  ("safely buildable meanwhile" per SQ-2).
CRITERIA_CLOSED=[] — AC-FR-06-01/02 NOT registered (SPONSOR_QUEUE SQ-2).
GAPS_REMAINING={AC-FR-06-01: [ARABIC_RTL, SERVED_APP_E2E, UI] and AC-FR-06-02: [SERVED_APP_E2E] — SQ-2;
                AC-FR-06-03: PRODUCTION; AC-FR-06-05: COUNSEL:REG-02_TELEMEDICINE}
FR-06: REACHABLE_TESTED / EVIDENCE_INCOMPLETE (unchanged counts)
```

## Build
- `video.py` + routes (all behind `_video_call`: the session actor must be a participant, the consultation REMOTE_VIDEO,
  and the REG-02 gate open — otherwise 404 / 409 / 403 REMOTE_CONSULTATION_NOT_OFFERED):
  `POST/GET /api/consultations/{id}/video/signal` — relays OFFER / ANSWER / ICE / SCREEN_OFFER / SCREEN_ANSWER / BYE to the
  OTHER participant only (media is peer-to-peer); `POST/GET …/video/quality` — NFR-03 record: a sample is compliant when
  ≥ 720p, or below 720p only with an adaptive-bitrate step-down reason (bandwidth/cpu); a non-compliant sample is audited.
- UI `/account/consultations/video?consultation=<id>`: no call control unless the served app says remote consultation is
  offered; 1280×720 minimum capture constraints; RTCPeerConnection with served signalling; screen share by `replaceTrack`
  on the video sender; quality reported every 5 s from `getStats` (frame size + `qualityLimitationReason`). Arabic RTL.

## Why AC-FR-06-01/02 are NOT registered
- SQ-2 (open): remote consultation is fail-closed until COUNSEL:REG-02; how AC-01/02 ("…from the served application")
  are accepted while the gate is closed is the Sponsor's decision.
- What is proven: served signalling between the two participants (gate opened IN-PROCESS as test setup) and the client
  wiring with stubbed media APIs. What is NOT proven: a real two-browser media path — that needs TURN relays and
  multi-instance signalling fan-out (PRODUCTION infrastructure) and, for a served proof, the gate open.

## Perturbations
```
P-VIDEO-GATE-OPEN           video path ignores the REG-02 gate       -> gate test FAILS         ARMED
P-VIDEO-NONPARTICIPANT      any tenant member can signal             -> relay test FAILS        ARMED
P-VIDEO-OWN-ECHO            a participant receives its own messages  -> relay test FAILS        ARMED
P-VIDEO-NO-STEP-DOWN-RULE   every sample compliant                   -> quality test FAILS      ARMED
P-VIDEO-UI-SD-CAPTURE       capture asks for 480p                    -> vitest FAILS            ARMED
P-VIDEO-UI-NO-GATE          page offers a call when not offered      -> vitest FAILS            ARMED
P-VIDEO-UI-NO-SCREEN        screen share never replaces the track    -> vitest FAILS            ARMED
PERTURBATIONS=7 ARMED=7 VACUOUS=0
```
