'use client'

/**
 * CO-06 — pre-visit intake with photos (MVC-EPC-D-001 D2p, R21.4).
 *
 * Before an upcoming appointment the owner tells the clinic why they are coming and may attach up to five photos. The server
 * holds ONE intake per booking (POST /api/bookings/{id}/intake) and refuses a second; once submitted, this page shows what the
 * veterinarian will read (GET …/intake) and each photo as a download. Owner, tenant and pet come from the session and the
 * booking on the server — the page sends only the answers and the photos. Arabic by default, right-to-left.
 */

import { FormEvent, useCallback, useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'
import { formatKsa } from '@/lib/ksaTime'

type Photo = { photo_id: string; filename: string; byte_size: number }
type Intake = { intake_id: string; booking_id: string; reason: string; symptoms_since: string | null;
  eating_normally: 'YES' | 'NO' | 'UNSURE'; current_medications: string; submitted_at: string; photos: Photo[] }

const MAX_PHOTOS = 5
const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')

const L = {
  title: { ar: 'استمارة ما قبل الزيارة', en: 'Pre-visit intake' },
  lead: { ar: 'أخبر العيادة بسبب الزيارة قبل موعدك. تُرسل الاستمارة مرة واحدة ولا يمكن تعديلها بعد الإرسال.',
    en: 'Tell the clinic why you are coming before your appointment. The intake is sent once and cannot be changed afterwards.' },
  reason: { ar: 'سبب الزيارة والأعراض', en: 'Reason for the visit and symptoms' },
  since: { ar: 'منذ متى بدأت الأعراض', en: 'Symptoms since' },
  eating: { ar: 'هل يأكل ويشرب بشكل طبيعي؟', en: 'Eating and drinking normally?' },
  YES: { ar: 'نعم', en: 'Yes' },
  NO: { ar: 'لا', en: 'No' },
  UNSURE: { ar: 'غير متأكد', en: 'Not sure' },
  meds: { ar: 'الأدوية الحالية', en: 'Current medications' },
  photos: { ar: 'صور (حتى خمس صور)', en: 'Photos (up to five)' },
  tooMany: { ar: 'يمكن إرفاق خمس صور كحد أقصى.', en: 'You can attach at most five photos.' },
  submit: { ar: 'إرسال الاستمارة', en: 'Send intake' },
  done: { ar: 'أُرسلت الاستمارة إلى العيادة.', en: 'The intake was sent to the clinic.' },
  submitted: { ar: 'الاستمارة المُرسلة', en: 'Submitted intake' },
  submittedAt: { ar: 'تاريخ الإرسال', en: 'Sent on' },
  none: { ar: 'لا يوجد', en: 'None' },
  download: { ar: 'تنزيل الصورة', en: 'Download photo' },
  notUpcoming: { ar: 'لا تُقبل الاستمارة إلا لموعد قادم ومحجوز.', en: 'An intake is accepted only for an upcoming booked appointment.' },
  already: { ar: 'سبق إرسال استمارة لهذا الموعد.', en: 'An intake was already sent for this appointment.' },
  rejected: { ar: 'تعذر قبول الاستمارة. تحقق من الحقول والصور (صور فقط).', en: 'The intake could not be accepted. Check the fields and photos (images only).' },
  failed: { ar: 'تعذر عرض الموعد.', en: 'The appointment could not be shown.' },
  back: { ar: 'العودة إلى مواعيدي', en: 'Back to my appointments' },
} as const

export default function PreVisitIntakePage({ params }: { params: { bookingId: string } }) {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  const t = (k: keyof typeof L) => L[k][isAr ? 'ar' : 'en']
  const base = `${apiBase}/api/bookings/${encodeURIComponent(params.bookingId)}/intake`

  const [state, setState] = useState<'loading' | 'form' | 'submitted' | 'failed'>('loading')
  const [intake, setIntake] = useState<Intake | null>(null)
  const [justSent, setJustSent] = useState(false)
  const [error, setError] = useState<keyof typeof L | null>(null)

  const load = useCallback(async () => {
    const r = await fetch(base, { credentials: 'include', cache: 'no-store' })
    if (r.status === 404) { setState('form'); return }
    if (!r.ok) { setState('failed'); return }
    setIntake(await r.json()); setState('submitted')
  }, [base])

  useEffect(() => { void load() }, [load])

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setError(null)
    const form = new FormData(e.currentTarget)
    const input = e.currentTarget.elements.namedItem('photos') as HTMLInputElement | null
    const files = Array.from(input?.files ?? []).filter(f => f.size > 0)
    if (files.length > MAX_PHOTOS) { setError('tooMany'); return }
    const body = new FormData()
    for (const k of ['reason', 'symptoms_since', 'eating_normally', 'current_medications']) body.set(k, String(form.get(k) ?? ''))
    files.forEach(f => body.append('photos', f))
    const r = await fetch(base, { method: 'POST', credentials: 'include', body })
    if (r.status === 201) { setIntake(await r.json()); setJustSent(true); setState('submitted'); return }
    const code = await r.json().then(j => j?.detail?.error).catch(() => undefined)
    setError(code === 'BOOKING_NOT_UPCOMING' ? 'notUpcoming' : code === 'INTAKE_ALREADY_SUBMITTED' ? 'already'
      : code === 'TOO_MANY_PHOTOS' ? 'tooMany' : 'rejected')
  }

  const day = (d: string) => formatKsa(`${d}T12:00:00+03:00`, lang, { dateStyle: 'medium' })

  return (
    <main className="stack" dir={isAr ? 'rtl' : 'ltr'} lang={isAr ? 'ar' : 'en'} data-testid="intake-page">
      <h1 className="title-lg">{t('title')}</h1>
      {state === 'failed' && <p role="alert">{t('failed')}</p>}
      {error && <p role="alert" data-testid="intake-error">{t(error)}</p>}

      {state === 'form' && (
        <form onSubmit={e => void submit(e)} aria-label={t('title')} data-testid="intake-form">
          <p>{t('lead')}</p>
          <label>{t('reason')}<textarea name="reason" required maxLength={500} /></label>
          <label>{t('since')}<input name="symptoms_since" type="date" /></label>
          <fieldset>
            <legend>{t('eating')}</legend>
            {(['YES', 'NO', 'UNSURE'] as const).map(v => (
              <label key={v}><input type="radio" name="eating_normally" value={v} required /> {t(v)}</label>
            ))}
          </fieldset>
          <label>{t('meds')}<textarea name="current_medications" maxLength={500} /></label>
          <label>{t('photos')}
            <input name="photos" type="file" multiple accept="image/jpeg,image/png,image/heic" data-testid="intake-photos" />
          </label>
          <button type="submit" className="button" data-testid="intake-submit">{t('submit')}</button>
        </form>
      )}

      {state === 'submitted' && intake && (
        <section aria-label={t('submitted')} data-testid="intake-submitted">
          {justSent && <p role="status" data-testid="intake-done">{t('done')}</p>}
          <h2>{t('submitted')}</h2>
          <dl>
            <dt>{t('reason')}</dt><dd data-testid="intake-reason">{intake.reason}</dd>
            <dt>{t('since')}</dt><dd>{intake.symptoms_since ? day(intake.symptoms_since) : t('none')}</dd>
            <dt>{t('eating')}</dt><dd data-testid="intake-eating" data-value={intake.eating_normally}>{t(intake.eating_normally)}</dd>
            <dt>{t('meds')}</dt><dd>{intake.current_medications || t('none')}</dd>
            <dt>{t('submittedAt')}</dt><dd>{formatKsa(intake.submitted_at, lang, { dateStyle: 'medium', timeStyle: 'short' })}</dd>
          </dl>
          <h3>{t('photos')}</h3>
          {intake.photos.length === 0 ? <p>{t('none')}</p> : (
            <ul>{intake.photos.map(p => (
              <li key={p.photo_id} data-testid="intake-photo">
                <span translate="no">{p.filename}</span>{' '}
                <a href={`${base}/photos/${encodeURIComponent(p.photo_id)}`} data-testid="intake-photo-download">{t('download')}</a>
              </li>
            ))}</ul>
          )}
        </section>
      )}

      <a className="button button-outline" href="/owner/appointments">{t('back')}</a>
    </main>
  )
}
