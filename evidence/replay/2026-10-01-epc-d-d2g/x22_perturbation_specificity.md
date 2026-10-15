# X-22 perturbation specificity (MVC-EPC-D-001 D2g, Sponsor R18 step 2) — 2026-10-01

## 1. Breadth diagnosis of the original 21-cell matrix under the UTC lapse reversion
Each cell ran U10 + D2f registration tests + D2g lapse tests with `licences.VetLicence.expires_at()` reverted to UTC midnight.
Every one of the 21 cells failed the SAME five tests (0 errors, 0 fixture/crash failures). None depends on the cell's instant:

| failing test | why it fails under UTC | semantic? | cell-dependent? |
|---|---|---|---|
| test_epc_d2g_x22_clinical_lapse.py::…[D+1-0000] | act at 00:00 Riyadh D+1 ADMITTED (200 vs 403) | yes (refusal semantics) | no — fixed 2031 instant |
| test_epc_d2g_x22_clinical_lapse.py::…[D+1-0259] | act at 02:59 Riyadh D+1 ADMITTED (200 vs 403) | yes | no — fixed 2031 instant |
| test_epc_d2g_x22_clinical_lapse.py::…[D+1-0300] | refused in both; reason string `+00:00` vs `+03:00` | format only | no |
| test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight | lapse instant equality | rule identity | no |
| test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act (U10 :178) | refused in both (+2 days); reason string `+00:00` vs `+03:00` | format only | no |

Why the 12:00 and 23:30 Riyadh cells failed: not because of their instants (there the UTC and Riyadh dates agree and a UTC
lapse refuses at the same moment), but because every cell carried the fixed-instant and format assertions above.
**Finding D2G-X22-PERTURBATION-BREADTH:** the 21/21 "FAIL" signature did not prove per-cell semantic discrimination; it is not
counted as such. The matrix was strengthened with a cell-sensitive probe (§2).

Raw per-cell output:
```
UTC          01:30 Riyadh      failed=5 errors=0 kinds=['OTHER']
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0000]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0259]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0300]
      test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight
      test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act
UTC          12:00 Riyadh      failed=5 errors=0 kinds=['OTHER']
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0000]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0259]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0300]
      test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight
      test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act
UTC          23:30 Riyadh      failed=5 errors=0 kinds=['OTHER']
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0000]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0259]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0300]
      test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight
      test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act
UTC          23:59 Riyadh D    failed=5 errors=0 kinds=['OTHER']
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0000]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0259]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0300]
      test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight
      test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act
UTC          00:00 Riyadh D+1  failed=5 errors=0 kinds=['OTHER']
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0000]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0259]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0300]
      test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight
      test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act
UTC          02:59 Riyadh D+1  failed=5 errors=0 kinds=['OTHER']
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0000]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0259]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0300]
      test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight
      test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act
UTC          03:00 Riyadh D+1  failed=5 errors=0 kinds=['OTHER']
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0000]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0259]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0300]
      test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight
      test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act
Asia/Riyadh  01:30 Riyadh      failed=5 errors=0 kinds=['OTHER']
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0000]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0259]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0300]
      test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight
      test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act
Asia/Riyadh  12:00 Riyadh      failed=5 errors=0 kinds=['OTHER']
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0000]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0259]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0300]
      test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight
      test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act
Asia/Riyadh  23:30 Riyadh      failed=5 errors=0 kinds=['OTHER']
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0000]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0259]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0300]
      test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight
      test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act
Asia/Riyadh  23:59 Riyadh D    failed=5 errors=0 kinds=['OTHER']
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0000]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0259]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0300]
      test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight
      test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act
Asia/Riyadh  00:00 Riyadh D+1  failed=5 errors=0 kinds=['OTHER']
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0000]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0259]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0300]
      test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight
      test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act
Asia/Riyadh  02:59 Riyadh D+1  failed=5 errors=0 kinds=['OTHER']
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0000]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0259]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0300]
      test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight
      test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act
Asia/Riyadh  03:00 Riyadh D+1  failed=5 errors=0 kinds=['OTHER']
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0000]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0259]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0300]
      test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight
      test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act
Asia/Dubai   01:30 Riyadh      failed=5 errors=0 kinds=['OTHER']
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0000]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0259]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0300]
      test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight
      test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act
Asia/Dubai   12:00 Riyadh      failed=5 errors=0 kinds=['OTHER']
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0000]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0259]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0300]
      test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight
      test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act
Asia/Dubai   23:30 Riyadh      failed=5 errors=0 kinds=['OTHER']
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0000]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0259]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0300]
      test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight
      test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act
Asia/Dubai   23:59 Riyadh D    failed=5 errors=0 kinds=['OTHER']
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0000]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0259]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0300]
      test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight
      test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act
Asia/Dubai   00:00 Riyadh D+1  failed=5 errors=0 kinds=['OTHER']
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0000]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0259]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0300]
      test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight
      test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act
Asia/Dubai   02:59 Riyadh D+1  failed=5 errors=0 kinds=['OTHER']
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0000]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0259]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0300]
      test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight
      test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act
Asia/Dubai   03:00 Riyadh D+1  failed=5 errors=0 kinds=['OTHER']
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0000]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0259]
      test_epc_d2g_x22_clinical_lapse.py::test_clinical_acts_lapse_at_riyadh_midnight_after_the_expiry_day[D+1-0300]
      test_epc_d2g_x22_clinical_lapse.py::test_the_licence_lapse_instant_is_riyadh_midnight
      test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act
restored
```

## 2. Cell-sensitive probe matrix (`x22_lapse_probe_matrix.py`, probe `test_epc_d2g_x22_cell_probe.py`)
Governed rule: `X22_LAPSE_PROBE_MATRIX[GOVERNED]=PASS cells=21 unexpected=0`.
UTC lapse reversion, run with `--expect-utc-signature` (exact expected failure set):
```
TZ=UTC          01:30 Riyadh      FAIL failed=['test_a_clinical_act_now_follows_the_riyadh_calendar[riyadh-yesterday-False]'] as-expected
TZ=UTC          12:00 Riyadh      PASS failed=[] as-expected
TZ=UTC          23:30 Riyadh      PASS failed=[] as-expected
TZ=UTC          23:59 Riyadh D    PASS failed=[] as-expected
TZ=UTC          00:00 Riyadh D+1  FAIL failed=['test_a_clinical_act_now_follows_the_riyadh_calendar[riyadh-yesterday-False]'] as-expected
TZ=UTC          02:59 Riyadh D+1  FAIL failed=['test_a_clinical_act_now_follows_the_riyadh_calendar[riyadh-yesterday-False]'] as-expected
TZ=UTC          03:00 Riyadh D+1  PASS failed=[] as-expected
TZ=Asia/Riyadh  01:30 Riyadh      FAIL failed=['test_a_clinical_act_now_follows_the_riyadh_calendar[riyadh-yesterday-False]'] as-expected
TZ=Asia/Riyadh  12:00 Riyadh      PASS failed=[] as-expected
TZ=Asia/Riyadh  23:30 Riyadh      PASS failed=[] as-expected
TZ=Asia/Riyadh  23:59 Riyadh D    PASS failed=[] as-expected
TZ=Asia/Riyadh  00:00 Riyadh D+1  FAIL failed=['test_a_clinical_act_now_follows_the_riyadh_calendar[riyadh-yesterday-False]'] as-expected
TZ=Asia/Riyadh  02:59 Riyadh D+1  FAIL failed=['test_a_clinical_act_now_follows_the_riyadh_calendar[riyadh-yesterday-False]'] as-expected
TZ=Asia/Riyadh  03:00 Riyadh D+1  PASS failed=[] as-expected
TZ=Asia/Dubai   01:30 Riyadh      FAIL failed=['test_a_clinical_act_now_follows_the_riyadh_calendar[riyadh-yesterday-False]'] as-expected
TZ=Asia/Dubai   12:00 Riyadh      PASS failed=[] as-expected
TZ=Asia/Dubai   23:30 Riyadh      PASS failed=[] as-expected
TZ=Asia/Dubai   23:59 Riyadh D    PASS failed=[] as-expected
TZ=Asia/Dubai   00:00 Riyadh D+1  FAIL failed=['test_a_clinical_act_now_follows_the_riyadh_calendar[riyadh-yesterday-False]'] as-expected
TZ=Asia/Dubai   02:59 Riyadh D+1  FAIL failed=['test_a_clinical_act_now_follows_the_riyadh_calendar[riyadh-yesterday-False]'] as-expected
TZ=Asia/Dubai   03:00 Riyadh D+1  PASS failed=[] as-expected
X22_LAPSE_PROBE_MATRIX[UTC_SIGNATURE]=PASS cells=21 unexpected=0
```
Determination: under the UTC reversion exactly the 9 cells whose Riyadh and UTC calendar dates differ (01:30, 00:00 D+1, 02:59 D+1
× UTC/Asia/Riyadh/Asia/Dubai hosts) fail, each ONLY on "a licence that expired on the Riyadh yesterday is refused now" (the act is
wrongly admitted); the 12 cells where the dates agree pass. Host TZ never changes the outcome. This — not the 21/21 matrix — is the
evidence that the UTC perturbation is ARMED for the intended semantic reason (P-D2G-X22-LAPSE-UTC-PROBE-MATRIX).
