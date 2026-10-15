'use client'

/**
 * CO-10 — visit summary and care plan (MVC-EPC-D-001 D2q, R21.4).
 *
 * The owner's summary of one completed consultation, exactly as the server assembles it (GET /api/owner/consultations/{id}/
 * summary): the outcome the veterinarian recorded, the prescriptions issued under this consultation, and the care plan the
 * veterinarian recorded (home-care instructions, follow-up date). Clinical text is shown as written; nothing is added or
 * inferred here. An incomplete visit has no summary yet. Arabic by default, right-to-left.
 */

import { useCallback, useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'
import { formatKsa } from '@/lib/ksaTime'

type Rx = { prescription_id: string; medication_name: string; dosage: string; instructions: string; status: string }
type Summary = {
  session_id: string
  pet: { pet_id: string; name: string | null }
  veterinarian: { user_id: string; name: string | null }
  mode: 'IN_PERSON' | 'REMOTE_VIDEO'
  visited_at: string
  outcome: { text: string; recorded_at: string }
  prescriptions: Rx[]
  care_plan: { instructions: string; follow_up_on: string | null; recorded_at: string } | null
}

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')

const L = {
  title: { ar: 'ملخص الزيارة وخطة الرعاية', en: 'Visit summary and care plan' },
  visit: { ar: 'الزيارة', en: 'Visit' },
  vet: { ar: 'الطبيب البيطري', en: 'Veterinarian' },
  inPerson: { ar: 'حضورية', en: 'In person' },
  video: { ar: 'مرئية', en: 'Video' },
  outcome: { ar: 'ملخص الطبيب', en: "Veterinarian's summary" },
  prescriptions: { ar: 'الأدوية الموصوفة في هذه الزيارة', en: 'Medicines prescribed at this visit' },
  noRx: { ar: 'لم تُوصف أدوية في هذه الزيارة.', en: 'No medicines were prescribed at this visit.' },
  plan: { ar: 'خطة الرعاية', en: 'Care plan' },
  noPlan: { ar: 'لم يسجّل الطبيب خطة رعاية لهذه الزيارة بعد.', en: 'The veterinarian has not recorded a care plan for this visit yet.' },
  followUp: { ar: 'موعد المتابعة', en: 'Follow-up' },
  noFollowUp: { ar: 'لا توجد متابعة محددة', en: 'No follow-up set' },
  notCompleted: { ar: 'لا يتوفر ملخص قبل اكتمال الزيارة.', en: 'A summary is available once the visit is completed.' },
  failed: { ar: 'تعذر عرض ملخص الزيارة.', en: 'The visit summary could not be shown.' },
  back: { ar: 'العودة إلى استشاراتي', en: 'Back to my consultations' },
} as const

export default function VisitSummaryPage({ params }: { params: { sessionId: string } }) {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  const t = (k: keyof typeof L) => L[k][isAr ? 'ar' : 'en']
  const [state, setState] = useState<'loading' | 'ready' | 'notCompleted' | 'failed'>('loading')
  const [s, setS] = useState<Summary | null>(null)

  const load = useCallback(async () => {
    const r = await fetch(`${apiBase}/api/owner/consultations/${encodeURIComponent(params.sessionId)}/summary`,
      { credentials: 'include', cache: 'no-store' })
    if (r.status === 409) { setState('notCompleted'); return }
    if (!r.ok) { setState('failed'); return }
    setS(await r.json()); setState('ready')
  }, [params.sessionId])

  useEffect(() => { void load() }, [load])

  const day = (d: string) => formatKsa(`${d}T12:00:00+03:00`, lang, { dateStyle: 'medium' })

  return (
    <main className="stack" dir={isAr ? 'rtl' : 'ltr'} lang={isAr ? 'ar' : 'en'} data-testid="visit-summary-page">
      <h1 className="title-lg">{t('title')}</h1>
      {state === 'failed' && <p role="alert">{t('failed')}</p>}
      {state === 'notCompleted' && <p role="status" data-testid="visit-not-completed">{t('notCompleted')}</p>}

      {state === 'ready' && s && (
        <article data-testid="visit-summary" aria-label={t('title')}>
          <h2>{s.pet.name ?? ''}</h2>
          <dl>
            <dt>{t('visit')}</dt>
            <dd>{formatKsa(s.visited_at, lang, { dateStyle: 'medium', timeStyle: 'short' })} · {t(s.mode === 'REMOTE_VIDEO' ? 'video' : 'inPerson')}</dd>
            <dt>{t('vet')}</dt><dd data-testid="visit-vet">{s.veterinarian.name ?? ''}</dd>
          </dl>

          <h3>{t('outcome')}</h3>
          <p data-testid="visit-outcome">{s.outcome.text}</p>

          <h3>{t('prescriptions')}</h3>
          {s.prescriptions.length === 0 ? <p data-testid="visit-no-prescriptions">{t('noRx')}</p> : (
            <ul>{s.prescriptions.map(rx => (
              <li key={rx.prescription_id} data-testid="visit-prescription" data-status={rx.status}>
                <strong>{rx.medication_name}</strong> {rx.dosage} — {rx.instructions}
              </li>
            ))}</ul>
          )}

          <h3>{t('plan')}</h3>
          {s.care_plan === null ? <p data-testid="visit-no-care-plan">{t('noPlan')}</p> : (
            <section data-testid="visit-care-plan">
              <p data-testid="care-plan-instructions">{s.care_plan.instructions}</p>
              <p>{t('followUp')}:{' '}
                <span data-testid="care-plan-follow-up" data-date={s.care_plan.follow_up_on ?? ''}>
                  {s.care_plan.follow_up_on ? day(s.care_plan.follow_up_on) : t('noFollowUp')}
                </span>
              </p>
            </section>
          )}
        </article>
      )}

      <a className="button button-outline" href="/owner/consultations">{t('back')}</a>
    </main>
  )
}
