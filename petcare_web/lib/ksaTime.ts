/**
 * KSA calendar for every date or time shown to a person (MVC-EPC-D-001 D2g, X-28 / Sponsor ruling R17.4). An instant is
 * always rendered on the Asia/Riyadh clock, never the viewer's host zone and never UTC, so a record made at 01:30 Riyadh
 * shows that Riyadh day everywhere. tests/governance-like guard: __tests__/epc-d2g-ksa-dates.test.ts.
 */
export const KSA_TIME_ZONE = 'Asia/Riyadh'

export function formatKsa(iso: string | number | Date, lang: string, options: Intl.DateTimeFormatOptions): string {
  const d = iso instanceof Date ? iso : new Date(iso)
  if (Number.isNaN(d.getTime())) return '—'
  return d.toLocaleString(lang === 'ar' ? 'ar-SA' : 'en-GB', { ...options, timeZone: KSA_TIME_ZONE })
}
