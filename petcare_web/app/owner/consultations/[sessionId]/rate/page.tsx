'use client'

/**
 * CO-13 — rate visit (MVC-EPC-D-001 D2r, R21.4).
 *
 * The owner rates one of their own completed consultations once: a score of 1 to 5 and an optional comment
 * (POST /api/owner/consultations/{id}/rating). Once rated, the page shows the rating as the server holds it — it cannot be changed.
 * The server decides whether the visit can be rated (completed, the owner's own); this page only reports its answer.
 * Arabic by default, right-to-left.
 */

import { FormEvent, useCallback, useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'

type Rating = { session_id: string; score: number; comment: string; rated_at: string }

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')

const L = {
  title: { ar: 'تقييم الزيارة', en: 'Rate visit' },
  lead: { ar: 'قيّم زيارتك من ١ إلى ٥. يُرسل التقييم مرة واحدة ولا يمكن تعديله.', en: 'Rate your visit from 1 to 5. A rating is sent once and cannot be changed.' },
  score: { ar: 'التقييم', en: 'Score' },
  comment: { ar: 'تعليق (اختياري)', en: 'Comment (optional)' },
  submit: { ar: 'إرسال التقييم', en: 'Send rating' },
  thanks: { ar: 'شكراً، تم تسجيل تقييمك.', en: 'Thank you, your rating was recorded.' },
  yours: { ar: 'تقييمك', en: 'Your rating' },
  of5: { ar: 'من ٥', en: 'out of 5' },
  notCompleted: { ar: 'يمكن تقييم الزيارة بعد اكتمالها.', en: 'A visit can be rated once it is completed.' },
  already: { ar: 'سبق تقييم هذه الزيارة.', en: 'This visit was already rated.' },
  rejected: { ar: 'تعذر قبول التقييم.', en: 'The rating could not be accepted.' },
  back: { ar: 'العودة إلى استشاراتي', en: 'Back to my consultations' },
} as const

export default function RateVisitPage({ params }: { params: { sessionId: string } }) {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  const t = (k: keyof typeof L) => L[k][isAr ? 'ar' : 'en']
  const base = `${apiBase}/api/owner/consultations/${encodeURIComponent(params.sessionId)}/rating`
  const digits = (n: number) => (isAr ? n.toLocaleString('ar-SA') : String(n))

  const [state, setState] = useState<'loading' | 'form' | 'rated'>('loading')
  const [rating, setRating] = useState<Rating | null>(null)
  const [justSent, setJustSent] = useState(false)
  const [error, setError] = useState<keyof typeof L | null>(null)

  const load = useCallback(async () => {
    const r = await fetch(base, { credentials: 'include', cache: 'no-store' })
    if (r.ok) { setRating(await r.json()); setState('rated'); return }
    setState('form')
  }, [base])

  useEffect(() => { void load() }, [load])

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setError(null)
    const f = new FormData(e.currentTarget)
    const r = await fetch(base, { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ score: Number(f.get('score')), comment: String(f.get('comment') ?? '') }) })
    if (r.status === 201) { setRating(await r.json()); setJustSent(true); setState('rated'); return }
    const code = await r.json().then(j => j?.detail?.error).catch(() => undefined)
    setError(code === 'VISIT_NOT_COMPLETED' ? 'notCompleted' : code === 'VISIT_ALREADY_RATED' ? 'already' : 'rejected')
  }

  return (
    <main className="stack" dir={isAr ? 'rtl' : 'ltr'} lang={isAr ? 'ar' : 'en'} data-testid="rate-page">
      <h1 className="title-lg">{t('title')}</h1>
      {error && <p role="alert" data-testid="rate-error">{t(error)}</p>}

      {state === 'form' && (
        <form onSubmit={e => void submit(e)} aria-label={t('title')} data-testid="rate-form">
          <p>{t('lead')}</p>
          <fieldset>
            <legend>{t('score')}</legend>
            {[1, 2, 3, 4, 5].map(n => (
              <label key={n}><input type="radio" name="score" value={n} required /> {digits(n)}</label>
            ))}
          </fieldset>
          <label>{t('comment')}<textarea name="comment" maxLength={500} /></label>
          <button type="submit" className="button" data-testid="rate-submit">{t('submit')}</button>
        </form>
      )}

      {state === 'rated' && rating && (
        <section aria-label={t('yours')} data-testid="rate-done">
          {justSent && <p role="status" data-testid="rate-thanks">{t('thanks')}</p>}
          <h2>{t('yours')}</h2>
          <p data-testid="rate-score" data-score={rating.score}>{digits(rating.score)} {t('of5')}</p>
          {rating.comment && <p data-testid="rate-comment">{rating.comment}</p>}
        </section>
      )}

      <a className="button button-outline" href="/owner/consultations">{t('back')}</a>
    </main>
  )
}
