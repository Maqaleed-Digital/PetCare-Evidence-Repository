# U27 · SQ-2 → AC-FR-06-01/02 — video capability accepted NON_PROD behind a default-OFF switch, 2026-09-26

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.2   UNIT=U27   BASE_MAIN=8fad3c6cd9c6c2757008d3c525b791d388d71cbf (U26 merged, PR #72)
BRANCH=build/u27-sq2-video-nonprod-acceptance
AUTHORITY=governance/sponsor_acts/MVC-SQ2-VIDEO-CAPABILITY-ACCEPTANCE-001.md
ACT_HASHES[SQ2]=7b698f111cd08fdabbf65f048e05fe330f72b99fae63f4fede6743b83f0e6219
AC-FR-06-01: gaps -> []  (EVIDENCED, environment NON_PROD)
AC-FR-06-02: gaps -> []  (EVIDENCED, environment NON_PROD)
AC-FR-06-03 (PRODUCTION) and AC-FR-06-05 (COUNSEL:REG-02_TELEMEDICINE): UNTOUCHED
```

## Text check (first, as required)
`ratified_text` of AC-FR-06-01 and AC-FR-06-02 is EMPTY; neither statement nor fails_if requires production
(AC-01: "a booked consultation cannot connect both parties with video; or screen sharing is unavailable in-session";
AC-02: "renders below 720p without an adaptive-bitrate step-down record"). FINDING SQ2-TEXT-REQUIRES-PRODUCTION: NOT raised.

## Build
- `video.py`: `SWITCH_ENV=PETCARE_VIDEO_CAPABILITY_ENABLED`, `SWITCH_DEFAULT=False`; only an explicit `true`/`1` is ON.
- `main.py _video_call`: the REG-02 gate is decided FIRST and unchanged (AC-FR-06-05 refusal identical); the switch is
  an additional later condition -> 403 `VIDEO_CAPABILITY_DISABLED`. Availability reports `video_capability`.
- Web video page offers call controls only when `offered` AND `video_capability === true`.
- Switch turned ON only in test configuration (`monkeypatch.setenv` in the tests); the REG-02 determination substituted
  in-process as in U22 (test setup, NOT counsel evidence). No production activation.

## Evidence registered (each item: `environment: NON_PROD`, `authority: … sha256 <SQ2>`)
| Criterion | Type | Ref |
|---|---|---|
| AC-FR-06-01 | SERVED_APP_E2E | test_sq2_video_nonprod.py::test_ac_fr_06_01_a_booked_video_consultation_connects_both_parties_with_screen_sharing |
| AC-FR-06-01 | UI | ARTEFACT petcare_web/__tests__/fr06-video-call.test.tsx sha256 fd3514b24b090a8f52e78ba09eb4357e232996c40130a8001aa3b832dda6aaff |
| AC-FR-06-01 | ARABIC_RTL | same artefact (asserts `dir="rtl"`, Arabic controls) |
| AC-FR-06-02 | SERVED_APP_E2E | test_sq2_video_nonprod.py::test_ac_fr_06_02_below_720p_needs_an_adaptive_bitrate_step_down_record |

Controls (not registered): switch off with the gate open -> refused; switch defaults OFF in every non-test configuration
(sweep of 17 tracked deployment/runtime files: Dockerfiles, cloudbuild*, .env.example, workflows, next.config) and the
root conftest does not set it.

## Perturbations
```
P-SWITCH-DEFAULT-ON        SWITCH_DEFAULT=True                       -> default-off test FAILS  ARMED (mandated)
P-SWITCH-BYPASSED          _video_call ignores the switch            -> FAILS  ARMED
P-CONFIG-TURNS-SWITCH-ON   Dockerfile ENV …ENABLED=true              -> FAILS  ARMED
P-NO-SCREEN-SHARE          SCREEN_OFFER/ANSWER removed               -> FAILS  ARMED
P-NO-STEP-DOWN-RULE        every sample compliant                    -> FAILS  ARMED
P-WEB-IGNORES-SWITCH       page ignores video_capability             -> vitest FAILS  ARMED
PERTURBATIONS=6 ARMED=6 VACUOUS=0
```
