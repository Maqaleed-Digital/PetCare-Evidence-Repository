'use client'

/**
 * FR-14 — prescription issue, documents and vet verification (MVC-BUILD-RUNNER-001 U9).
 *
 * AC-FR-14-01 (UI): a veterinarian issues a prescription, attaches its documents and
 * verifies it; dispensing happens from /pharmacy. AC-FR-14-04 (UI): when the vet's live
 * practitioner authority is not in force, the prescribing control is PRESENTED as unavailable
 * with the reason — the attribute and its expiry — instead of failing on submit
 * (REQ-MVC-8.38). The served API refuses regardless; this page never sends an actor or tenant.
 * Route: /vet/prescriptions (middleware: vet, admin). Arabic default, RTL.
 */

import { FormEvent, useCallback, useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'

type Authority = { in_force: boolean; reason: string | null }
type Rx = { prescription_id: string; pet_id: string; medication_name: string; dosage: string; status: string }

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
const call = (path: string, init?: RequestInit) =>
  fetch(`${apiBase}${path}`, { credentials: 'include', cache: 'no-store', ...init })

const L = {
  kicker: { ar: 'بوابة الطبيب البيطري', en: 'Veterinarian portal' },
  title: { ar: 'الوصفات الطبية', en: 'Prescriptions' },
  issue: { ar: 'إصدار وصفة', en: 'Issue a prescription' },
  unavailable: { ar: 'إصدار الوصفات غير متاح', en: 'Prescribing is unavailable' },
  attribute: { ar: 'الصفة المطلوبة: طبيب بيطري مرخّص', en: 'Required attribute: licensed veterinarian' },
  pet: { ar: 'الحيوان', en: 'Pet' },
  session: { ar: 'الاستشارة', en: 'Consultation' },
  medication: { ar: 'الدواء', en: 'Medication' },
  dosage: { ar: 'الجرعة', en: 'Dosage' },
  instructions: { ar: 'التعليمات', en: 'Instructions' },
  awaiting: { ar: 'بانتظار التحقق', en: 'Awaiting verification' },
  none: { ar: 'لا توجد وصفات بانتظار التحقق.', en: 'No prescriptions awaiting verification.' },
  verify: { ar: 'تحقق', en: 'Verify' },
  attach: { ar: 'إرفاق مستند', en: 'Attach a document' },
  error: { ar: 'تعذر إكمال الطلب', en: 'The request could not be completed' },
} as const

/** "expired at 2026-09-22T10:00:00+00:00" -> the reason with a localised expiry date. */
function reasonText(reason: string | null, isAr: boolean): string {
  if (!reason) return ''
  const m = reason.match(/^(expired at|revoked at|not yet effective \(from) (.+?)\)?$/)
  if (!m) return reason === 'no authority granted' ? (isAr ? 'لا توجد صلاحية ممنوحة' : 'No authority granted') : reason
  const when = new Date(m[2]).toLocaleString(isAr ? 'ar-SA' : 'en-GB', { dateStyle: 'medium', timeStyle: 'short' })
  const label = { 'expired at': isAr ? 'انتهت في' : 'Expired at', 'revoked at': isAr ? 'أُلغيت في' : 'Revoked at',
    'not yet effective (from': isAr ? 'تسري اعتباراً من' : 'Effective from' }[m[1]]
  return `${label} ${when}`
}

export default function VetPrescriptionsPage() {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  const t = (k: keyof typeof L) => L[k][isAr ? 'ar' : 'en']
  const [authority, setAuthority] = useState<Authority | null>(null)
  const [awaiting, setAwaiting] = useState<Rx[]>([])
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    const [a, q] = await Promise.all([call('/api/practitioners/me/authority'),
      call('/api/prescriptions/queue/awaiting-verification')])
    if (a.ok) setAuthority(await a.json())
    if (q.ok) setAwaiting(await q.json())
  }, [])

  useEffect(() => { void load() }, [load])

  const canPrescribe = authority?.in_force === true

  async function issue(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (!canPrescribe) return
    const f = new FormData(e.currentTarget)
    const body = Object.fromEntries(['pet_id', 'session_id', 'medication_name', 'dosage', 'instructions']
      .map(k => [k, String(f.get(k) ?? '').trim()]))
    const r = await call('/api/prescriptions', { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body) })
    setError(r.ok ? '' : t('error'))
    if (r.ok) await load()
  }

  async function verify(id: string) {
    const r = await call(`/api/prescriptions/${id}/verify`, { method: 'POST' })
    setError(r.ok ? '' : t('error'))
    await load()
  }

  async function attach(id: string, file: File | undefined) {
    if (!file) return
    const fd = new FormData()
    fd.append('file', file)
    const r = await call(`/api/prescriptions/${id}/documents`, { method: 'POST', body: fd })
    setError(r.ok ? '' : t('error'))
  }

  return (
    <main className="stack" dir={isAr ? 'rtl' : 'ltr'}>
      <div>
        <div className="kicker">{t('kicker')}</div>
        <h1 className="title-lg">{t('title')}</h1>
      </div>
      <form onSubmit={issue} className="card stack" aria-label={t('issue')}>
        <h2 className="title-md">{t('issue')}</h2>
        {authority && !canPrescribe && (
          <div role="status" data-testid="prescribing-unavailable">
            <strong>{t('unavailable')}</strong>
            <div>{t('attribute')}</div>
            <div data-testid="authority-reason">{reasonText(authority.reason, isAr)}</div>
          </div>
        )}
        <fieldset disabled={!canPrescribe} className="stack">
          <label>{t('pet')}<input name="pet_id" required /></label>
          <label>{t('session')}<input name="session_id" required /></label>
          <label>{t('medication')}<input name="medication_name" required /></label>
          <label>{t('dosage')}<input name="dosage" required /></label>
          <label>{t('instructions')}<input name="instructions" required /></label>
          <button type="submit" className="btn" data-testid="issue-button">{t('issue')}</button>
        </fieldset>
      </form>
      <section className="card stack">
        <h2 className="title-md">{t('awaiting')}</h2>
        {awaiting.length === 0 && <p className="muted">{t('none')}</p>}
        {awaiting.map(rx => (
          <div key={rx.prescription_id} data-testid="awaiting-item" className="row">
            <span>{rx.medication_name} · {rx.dosage}</span>
            <label>{t('attach')}<input type="file" accept="application/pdf,image/jpeg,image/png,image/heic"
              onChange={e => void attach(rx.prescription_id, e.currentTarget.files?.[0])} /></label>
            <button type="button" className="btn" disabled={!canPrescribe}
              onClick={() => void verify(rx.prescription_id)}>{t('verify')}</button>
          </div>
        ))}
      </section>
      {error && <p role="alert">{error}</p>}
    </main>
  )
}
