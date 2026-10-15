'use client'

/**
 * J-V2 — CV-02 calendar and availability (MVC-EPC-D-001 D3b, R21.4).
 *
 * The veterinarian publishes their weekly schedule on the Asia/Riyadh clock: per weekday, whether they work and from when to
 * when (30-minute grid). Publishing makes a new version (PUT /api/vet/availability); owners can then book only those slots.
 * Existing bookings are never moved. Until the first publication the clinic default hours apply, and the page says so.
 * One window per weekday here; the server validates the schedule. Arabic by default, right-to-left.
 */

import { FormEvent, useCallback, useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'

type Window = { weekday: number; opens: string; closes: string }
type Availability = { plan_id: string | null; published_at: string | null; default_hours: boolean; windows: Window[] }

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
// Python weekday(): 0 = Monday … 6 = Sunday. Shown in the Saudi week order, Sunday first.
const ORDER = [6, 0, 1, 2, 3, 4, 5]
const DAYS = {
  ar: ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد'],
  en: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
}
const TIMES = Array.from({ length: 48 }, (_, i) => `${String(Math.floor(i / 2)).padStart(2, '0')}:${i % 2 ? '30' : '00'}`)

const L = {
  title: { ar: 'التقويم والتوفر', en: 'Calendar and availability' },
  lead: { ar: 'حدّد أيام عملك وساعاتها بتوقيت الرياض. لا تُغيّر المواعيد المحجوزة مسبقاً.', en: 'Set your working days and hours (Riyadh time). Existing bookings are not changed.' },
  defaults: { ar: 'لم تنشر جدولك بعد؛ تُطبّق ساعات العيادة الافتراضية (٩:٠٠–١٧:٠٠).', en: 'You have not published a schedule yet; the clinic default hours (09:00–17:00) apply.' },
  published: { ar: 'نُشر الجدول. يحجز المالكون الآن ضمن هذه الساعات فقط.', en: 'Schedule published. Owners can now book within these hours only.' },
  works: { ar: 'يوم عمل', en: 'Working day' },
  from: { ar: 'من', en: 'From' },
  to: { ar: 'إلى', en: 'To' },
  publish: { ar: 'نشر الجدول', en: 'Publish schedule' },
  invalid: { ar: 'تعذر نشر الجدول: تأكد أن وقت البداية قبل النهاية.', en: 'The schedule could not be published: check that each start is before its end.' },
  failed: { ar: 'تعذر عرض الجدول.', en: 'The schedule could not be shown.' },
} as const

export default function VetAvailabilityPage() {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  const t = (k: keyof typeof L) => L[k][isAr ? 'ar' : 'en']
  const [current, setCurrent] = useState<Availability | null>(null)
  const [days, setDays] = useState<Record<number, Window | null>>({})
  const [state, setState] = useState<'idle' | 'published' | 'invalid' | 'failed'>('idle')

  const load = useCallback(async () => {
    const r = await fetch(`${apiBase}/api/vet/availability`, { credentials: 'include', cache: 'no-store' })
    if (!r.ok) { setState('failed'); return }
    const a: Availability = await r.json()
    setCurrent(a)
    setDays(Object.fromEntries(ORDER.map(d => [d, a.windows.find(w => w.weekday === d) ?? null])))
  }, [])

  useEffect(() => { void load() }, [load])

  async function publish(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const windows = ORDER.map(d => days[d]).filter((w): w is Window => !!w)
    const r = await fetch(`${apiBase}/api/vet/availability`, { method: 'PUT', credentials: 'include',
      headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ windows }) })
    if (!r.ok) { setState('invalid'); return }
    setState('published')
    await load()
  }

  const set = (d: number, w: Window | null) => setDays(prev => ({ ...prev, [d]: w }))

  return (
    <main className="stack" dir={isAr ? 'rtl' : 'ltr'} lang={isAr ? 'ar' : 'en'} data-testid="vet-availability">
      <h1 className="title-lg">{t('title')}</h1>
      <p>{t('lead')}</p>
      {state === 'failed' && <p role="alert">{t('failed')}</p>}
      {state === 'invalid' && <p role="alert" data-testid="availability-invalid">{t('invalid')}</p>}
      {state === 'published' && <p role="status" data-testid="availability-published">{t('published')}</p>}
      {current?.default_hours && state !== 'published' && <p data-testid="availability-defaults">{t('defaults')}</p>}

      {current && (
        <form onSubmit={e => void publish(e)} data-testid="availability-form">
          {ORDER.map(d => {
            const w = days[d]
            return (
              <fieldset key={d} data-testid="availability-day" data-weekday={d} data-works={w ? 'true' : 'false'}>
                <legend>{DAYS[isAr ? 'ar' : 'en'][d]}</legend>
                <label><input type="checkbox" name={`works-${d}`} checked={!!w}
                  onChange={e => set(d, e.target.checked ? { weekday: d, opens: '09:00', closes: '17:00' } : null)} /> {t('works')}</label>
                {w && (
                  <>
                    <label>{t('from')} <select name={`opens-${d}`} value={w.opens} onChange={e => set(d, { ...w, opens: e.target.value })}>
                      {TIMES.map(x => <option key={x} value={x}>{x}</option>)}</select></label>
                    <label>{t('to')} <select name={`closes-${d}`} value={w.closes} onChange={e => set(d, { ...w, closes: e.target.value })}>
                      {TIMES.map(x => <option key={x} value={x}>{x}</option>)}</select></label>
                  </>
                )}
              </fieldset>
            )
          })}
          <button type="submit" className="button" data-testid="availability-publish">{t('publish')}</button>
        </form>
      )}
    </main>
  )
}
