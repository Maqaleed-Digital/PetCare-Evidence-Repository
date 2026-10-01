# MVC-EPC-D-001 D2g — calendar-date sweep (Sponsor ruling R17.4), 2026-10-01

Scope: canonical backend (`petcare_api`, `petcare_runtime/src`, SQL in `petcare_api/*.py` and `petcare_runtime/migrations`) and
canonical web (`petcare_web/app`, `components`, `lib`). The frozen prototype `petcare-web` is out of scope (X-24, not extended).
Patterns: backend `\.date\(\)|date\.today\(\)|utcnow\(\)|strftime\(|isoformat\(\)\[:10\]|\.today\(\)`, SQL
`current_date|::date|date_trunc|now\(\)::|localtime`; web `toISOString().slice|split|substring`, `toLocale(Date|Time)?String(`,
`getDate()|getFullYear()|getMonth()`, `Intl.DateTimeFormat`, `type="date"`. Every hit was read.
CP1 before the sweep: 15 (X-28 already assigned). CP1 after: 16 (+X-29).

| path:line (at D2g base c0d34fa) | behaviour | disposition |
|---|---|---|
| petcare_api/orders.py:90, :95 | receipt "Issued"/"تاريخ الإصدار" = `issued_at.date()` (UTC date) | **FIXED-D2g** (X-28): `ksa_calendar.ksa_date`; test `test_epc_d2g_x28_ksa_dates.py::test_the_receipt_issue_date_is_the_riyadh_date`; perturbation P-D2G-X28-RECEIPT-UTC |
| petcare_api/reminders.py:73 | reminder text due date = `due_at.date()` (UTC date) | **FIXED-D2g** (X-28): `ksa_date`; test `…::test_the_reminder_due_date_is_the_riyadh_date`; perturbation P-D2G-X28-REMINDER-UTC |
| petcare_api/licences.py:84 `VetLicence.expires_at()` -> main.py clinical-act recheck, grant expiry | lapse at next UTC midnight | **FIXED-D2g** (X-22, R17.2): next Asia/Riyadh midnight; test `test_epc_d2g_x22_clinical_lapse.py`; perturbation P-D2G-X22-LAPSE-UTC |
| petcare_api/main.py:2873 | antimicrobial report `period` = `issued_at.strftime("%Y-%m")` (UTC month) | **LEDGERED X-29** (CP1): frozen FR-30 assertion test_fr30_compliance.py:122 pins the UTC month; only R17.2's assertion change is authorised |
| petcare_api/licences.py:38, routers/auth.py:516, both repositories' submit | licence validity | already Asia/Riyadh (D2f, R16.3) |
| petcare_api/bookings.py:76, :78 | booking day / grid | already Asia/Riyadh (`CLINIC_ZONE`) |
| petcare_api/routers/auth.py:509, petcare_api/main.py:2120 | parse a user-entered `YYYY-MM-DD` | NOT-A-CALENDAR-DATE derivation: the date is the person's input, no instant is converted |
| petcare_runtime/src/petcare/pharmacy/models.py:14; partner_network/{service,catalog_service,contracts_service}.py | ISO UTC timestamp strings (`…Z`) | NOT-A-CALENDAR-DATE: an instant recorded in UTC, not a calendar date |
| SQL (`current_date`, `::date`, `date_trunc`, `localtime`) | — | no hits |
| petcare_web/app/owner/notifications/page.tsx:48 | `toLocaleString` without timeZone (viewer host clock) | **FIXED-D2g**: `formatKsa` |
| petcare_web/app/owner/recalls/page.tsx:52 | same | **FIXED-D2g**: `formatKsa` |
| petcare_web/app/owner/deliveries/page.tsx:50 | same | **FIXED-D2g**: `formatKsa` |
| petcare_web/app/vet/prescriptions/page.tsx:48 | same | **FIXED-D2g**: `formatKsa` |
| petcare_web/app/pharmacy/page.tsx:65 | same | **FIXED-D2g**: `formatKsa` |
| petcare_web/components/ConsentStateView.tsx:19 | same | **FIXED-D2g**: `formatKsa` |
| petcare_web/components/account/AccountCenter.tsx:113 | same | **FIXED-D2g**: `formatKsa` |
| petcare_web/app/owner/{appointments,consultations,consultations/messages}/page.tsx; app/owner/book/page.tsx:48 | already `timeZone: 'Asia/Riyadh'` | none |
| petcare_web/app/owner/orders/page.tsx:61, deliveries/page.tsx:51 | number `toLocaleString` (money, °C) | NOT-A-CALENDAR-DATE |
| petcare_web/app/api/health/route.ts:7, register/page.tsx:89 | `toISOString()` instant | NOT-A-CALENDAR-DATE: an instant sent to the server |
| petcare_web pets/page.tsx:187, register/page.tsx:186 `type="date"` | person enters a date | NOT-A-CALENDAR-DATE derivation |

Web evidence for the seven FIXED sites (assumption D2G-WEB-SITES-VIA-ONE-FORMATTER): one formatter `lib/ksaTime.formatKsa`
(Asia/Riyadh, caller cannot override) with a behaviour test at 01:30 Riyadh under host TZ=UTC, Asia/Riyadh and Asia/Dubai,
plus a source guard that fails on any date `toLocale*String` call without `timeZone` in the canonical app
(`petcare_web/__tests__/epc-d2g-ksa-dates.test.ts`); perturbations P-D2G-WEB-KSA-FORMAT-HOST-CLOCK and P-D2G-WEB-RAW-DATE-RENDER.
