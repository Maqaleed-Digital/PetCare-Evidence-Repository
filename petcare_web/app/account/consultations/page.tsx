'use client'

/**
 * FR-06 — the caller's consultations (MVC-BUILD-RUNNER-001 U11).
 *
 * AC-FR-06-04: each consultation with its participants and outcome, from the served, durable record.
 * AC-FR-06-05 (COUNSEL:REG-02_TELEMEDICINE): remote veterinary consultation is NOT offered until the
 * KSA telemedicine counsel determination is recorded. The served API says whether it is offered; while
 * it is not, this page shows why and presents NO remote/video control at all.
 * Route: /account/consultations. Arabic default, RTL.
 */

import { useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'

type Outcome = { outcome: string; recorded_by_actor_id: string; recorded_at: string }
type Consultation = { session_id: string; pet_id: string; mode: string; status: string; created_at: string; outcome: Outcome | null }
type Remote = { offered: boolean; reason?: string; dependency?: string }

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')

const L = {
  title: { ar: 'استشاراتي', en: 'My consultations' },
  none: { ar: 'لا توجد استشارات.', en: 'No consultations.' },
  remoteOff: { ar: 'الاستشارة البيطرية عن بُعد غير متاحة حالياً إلى حين صدور الرأي القانوني المعتمد بشأن الطب البيطري عن بُعد في المملكة.',
    en: 'Remote veterinary consultation is not offered until the KSA telemedicine counsel determination is recorded.' },
  IN_PERSON: { ar: 'حضورية', en: 'In person' },
  REMOTE_VIDEO: { ar: 'عن بُعد', en: 'Remote' },
  REQUESTED: { ar: 'مطلوبة', en: 'Requested' },
  COMPLETED: { ar: 'مكتملة', en: 'Completed' },
  outcome: { ar: 'النتيجة', en: 'Outcome' },
  error: { ar: 'تعذر تحميل الاستشارات', en: 'Consultations could not be loaded' },
} as const

export default function ConsultationsPage() {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  const t = (k: keyof typeof L) => L[k][isAr ? 'ar' : 'en']
  const [items, setItems] = useState<Consultation[]>([])
  const [remote, setRemote] = useState<Remote | null>(null)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    void (async () => {
      try {
        const r = await fetch(`${apiBase}/api/consultations`, { credentials: 'include', cache: 'no-store' })
        if (!r.ok) { setFailed(true); return }
        const body = await r.json()
        setItems(body.consultations)
        setRemote(body.remote)
      } catch { setFailed(true) }
    })()
  }, [])

  const label = (k: string) => (k in L ? t(k as keyof typeof L) : k)

  return (
    <main className="stack" dir={isAr ? 'rtl' : 'ltr'}>
      <h1 className="title-lg">{t('title')}</h1>
      {remote && !remote.offered && <p role="status" data-testid="remote-not-offered">{t('remoteOff')}</p>}
      {failed && <p role="alert">{t('error')}</p>}
      {!failed && items.length === 0 && <p className="muted">{t('none')}</p>}
      {items.map(c => (
        <section key={c.session_id} className="card" data-testid="consultation">
          <div>{label(c.mode)} · {label(c.status)}</div>
          {c.outcome && <div data-testid="consultation-outcome">{t('outcome')}: {c.outcome.outcome}</div>}
        </section>
      ))}
    </main>
  )
}
