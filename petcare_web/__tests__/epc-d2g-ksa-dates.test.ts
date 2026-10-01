/**
 * MVC-EPC-D-001 D2g — X-28 / R17.4 calendar-date sweep (web). Every date or time shown to a person is rendered on the
 * Asia/Riyadh clock through lib/ksaTime.formatKsa, so the viewer's host zone never changes the day shown.
 *  (1) behaviour: an instant at 01:30 Riyadh (the UTC date is still the previous day) shows the Riyadh day under host
 *      TZ=UTC and TZ=Asia/Riyadh alike;
 *  (2) guard: no date-formatting toLocale*String call in the canonical app omits a timeZone (the D2g sweep found seven).
 */
import fs from 'node:fs'
import path from 'node:path'
import { afterEach, describe, expect, it } from 'vitest'
import { formatKsa, KSA_TIME_ZONE } from '@/lib/ksaTime'

const AT_0130_RIYADH = '2031-03-09T22:30:00Z'
const original = process.env.TZ
afterEach(() => { process.env.TZ = original })

describe('formatKsa (D2g, X-28)', () => {
  for (const host of ['UTC', 'Asia/Riyadh', 'Asia/Dubai']) {
    it(`renders the Riyadh day under host TZ=${host}`, () => {
      process.env.TZ = host
      expect(formatKsa(AT_0130_RIYADH, 'en', { year: 'numeric', month: '2-digit', day: '2-digit' })).toBe('10/03/2031')
      expect(formatKsa(AT_0130_RIYADH, 'en', { hour: '2-digit', minute: '2-digit', hourCycle: 'h23' })).toBe('01:30')
      expect(formatKsa(AT_0130_RIYADH, 'ar', { day: 'numeric', numberingSystem: 'latn' })).toBe('10')
    })
  }

  it('is pinned to Asia/Riyadh even if a caller passes another zone', () => {
    expect(KSA_TIME_ZONE).toBe('Asia/Riyadh')
    expect(formatKsa(AT_0130_RIYADH, 'en', { day: '2-digit', timeZone: 'UTC' })).toBe('10')
    expect(formatKsa('not a date', 'en', { day: '2-digit' })).toBe('—')
  })
})

describe('no date is rendered on the host clock (D2g sweep guard)', () => {
  const root = path.resolve(__dirname, '..')
  const files: string[] = []
  const walk = (d: string) => {
    for (const e of fs.readdirSync(d, { withFileTypes: true })) {
      const p = path.join(d, e.name)
      if (e.isDirectory()) { if (!['node_modules', '.next', '__tests__', 'e2e', 'e2e-full'].includes(e.name)) walk(p) }
      else if (/\.(tsx?|jsx?)$/.test(e.name)) files.push(p)
    }
  }
  for (const d of ['app', 'components', 'lib']) walk(path.join(root, d))

  it('scans the canonical app', () => { expect(files.length).toBeGreaterThan(40) })

  it('every date-formatting toLocale*String call names a timeZone', () => {
    const offenders: string[] = []
    const DATE_KEYS = /\b(dateStyle|timeStyle|year|month|day|hour|minute|weekday)\b/
    for (const f of files) {
      const src = fs.readFileSync(f, 'utf8')
      for (const m of src.matchAll(/toLocale(Date|Time)?String\(/g)) {
        let depth = 0, i = (m.index ?? 0) + m[0].length - 1, end = i
        for (; end < src.length; end++) { if (src[end] === '(') depth++; else if (src[end] === ')' && --depth === 0) break }
        const call = src.slice(i, end + 1)
        const isDate = DATE_KEYS.test(call) || /new Date\([^)]*\)\s*\.\s*$/.test(src.slice(Math.max(0, i - 60), i - m[0].length + 1))
        if (isDate && !/timeZone/.test(call)) offenders.push(`${path.relative(root, f)}:${src.slice(0, m.index).split('\n').length}`)
      }
    }
    expect(offenders).toEqual([])
  })
})
