# U29 · AC-FR-06 video switch — default-off proof hardened (loader-first, whole-tree discovery), 2026-09-27

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.3   UNIT=U29   BASE_MAIN=630cbad295f920ccda42cf5556c16490f0383cee (U28 merged, PR #76)
BRANCH=build/u29-video-default-off-hardening
SCOPE=control hardening only; AC-FR-06-01/02 evidence (U27, SQ-2) unchanged; no production configuration touched
```

## Historical defect, stated factually
The U27 test did NOT hold a hard-coded list of 17 filenames. It matched `git ls-files` against configuration-family
filename patterns (Dockerfile*, cloudbuild*, .env*, compose, workflows, next.config, .tf/.tfvars, app.yaml, Procfile);
17 was the number of tracked files matching at v1.2. The defect was PATTERN INCOMPLETENESS: a new tracked source
outside those families (e.g. `ops/profiles/staging-runtime.yaml`) could set the switch without being examined.

## Configuration authority (recorded)
The switch has one reader, `video.capability_enabled(env)`; the served app calls it with the process environment
(`main.py`: availability and `_video_call`). There is no settings file or source registry. A repository-defined
profile is therefore any tracked file able to place the variable in a process environment, whatever its name/format.

## Hardened proof (`test_sq2_video_nonprod.py::test_the_video_switch_defaults_off_in_every_non_test_configuration`)
1. LOADER (primary): the default runtime profile — a fresh interpreter with no test configuration — resolves OFF via
   `capability_enabled(os.environ)`; and the `PETCARE_*` profile each tracked source defines is passed through the same
   loader and must resolve OFF.
2. DISCOVERY (defence in depth): every tracked file (3,842 at this head), not filename patterns. Every mention of the
   switch must carry a readable value (KEY=v, KEY: v, JSON, Dockerfile `ENV KEY v`, CLI `--set-env-vars`, k8s
   name/value, shell export); a mention with no readable value — e.g. a second code-level reader — fails closed.
3. Exclusions are by RULE, never by filename: test code (may switch the capability on for itself), the module that
   defines the switch (`video.py`, derived from the import), and record trees no deployment loads (evidence/,
   requirements/, governance/). The root `conftest.py` is scanned and must not mention the switch.
Why complete for the current architecture: the only way the switch becomes ON is an environment value reaching the one
loader; every in-repo source of environment values is a tracked file, and every tracked non-test, non-record file is
resolved through that loader. Values set outside the repository (a platform console) are production configuration,
not authorized by SQ-2 and not in repository scope.

## Perturbations — `evidence/replay/2026-09-27/perturb_u29.py` (committed, executable)
```
P-NEW-TRACKED-PROFILE-ENABLES-VIDEO  NEW tracked ops/profiles/staging-runtime.yaml (outside the v1.2 pattern
                                     families — asserted by the runner) sets the switch "true"      -> FAILS  ARMED
                                     failure names the file: ('ops/profiles/staging-runtime.yaml', 'resolves ON');
                                     no filename was added to any list
P-NEW-TRACKED-SECOND-READER          NEW tracked petcare_api/video_override.py reads the switch directly -> FAILS ARMED
P-SWITCH-DEFAULT-ON                  SWITCH_DEFAULT=True                                               -> FAILS ARMED
PERTURBATIONS=3 ARMED=3 VACUOUS=0   (new files staged with git add, then removed from index and disk)
```
