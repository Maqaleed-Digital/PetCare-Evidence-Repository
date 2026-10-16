'use client'

/**
 * J-V2 — CV-03 unified queue (MVC-EPC-D-001 D3b, R21.4).
 *
 * The veterinarian's own work as the server holds it (GET /api/vet/queue): upcoming booked appointments, soonest first, with the
 * pet, the owner, the reason and whether the owner sent a pre-visit intake; and their consultations not yet completed. Nothing
 * of another veterinarian's appears, and nothing is invented: an empty queue says it is empty. Arabic by default, right-to-left.
 */

import { useCallback, useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'
import { formatKsa } from '@/lib/ksaTime'

type Appointment = { booking_id: string; starts_at: string; mode: string; pet: { name: string | null }; owner_name: string | null;
  reason: string; intake_submitted: boolean }
type OpenConsultation = { session_id: string; created_at: string; mode: string; pet: { name: string | null }; owner_name: string | null }
type Queue = { appointments: Appointment[]; open_consultations: OpenConsultation[] }

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')

const L = {
  title: { ar: 'قائمة العمل الموحّدة', en: 'Unified queue' },
  appointments: { ar: 'المواعيد القادمة', en: 'Upcoming appointments' },
  noAppointments: { ar: 'لا توجد مواعيد قادمة.', en: 'No upcoming appointments.' },
  open: { ar: 'استشارات لم تكتمل', en: 'Consultations not yet completed' },
  noOpen: { ar: 'لا توجد استشارات مفتوحة.', en: 'No open consultations.' },
  owner: { ar: 'المالك', en: 'Owner' },
  inClinic: { ar: 'في العيادة', en: 'In clinic' },
  video: { ar: 'مرئية', en: 'Video' },
  intake: { ar: 'أرسل المالك استمارة ما قبل الزيارة', en: 'Pre-visit intake received' },
  noIntake: { ar: 'لا توجد استمارة ما قبل الزيارة', en: 'No pre-visit intake' },
  failed: { ar: 'تعذر عرض القائمة.', en: 'The queue could not be shown.' },
} as const

export default function VetQueuePage() {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  const t = (k: keyof typeof L) => L[k][isAr ? 'ar' : 'en']
  const [q, setQ] = useState<Queue | null>(null)
  const [failed, setFailed] = useState(false)

  const load = useCallback(async () => {
    const r = await fetch(`${apiBase}/api/vet/queue`, { credentials: 'include', cache: 'no-store' })
    if (!r.ok) { setFailed(true); return }
    setQ(await r.json())
  }, [])
  useEffect(() => { void load() }, [load])

  const when = (iso: string) => formatKsa(iso, lang, { weekday: 'long', day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit' })
  const mode = (m: string) => t(m === 'VIDEO' || m === 'REMOTE_VIDEO' ? 'video' : 'inClinic')

  return (
    <main className="stack" dir={isAr ? 'rtl' : 'ltr'} lang={isAr ? 'ar' : 'en'} data-testid="vet-queue">
      <h1 className="title-lg">{t('title')}</h1>
      {failed && <p role="alert">{t('failed')}</p>}
      {q && (
        <>
          <h2>{t('appointments')}</h2>
          {q.appointments.length === 0 ? <p data-testid="queue-no-appointments">{t('noAppointments')}</p> : (
            <ol>{q.appointments.map(a => (
              <li key={a.booking_id} data-testid="queue-appointment" data-booking={a.booking_id} data-intake={a.intake_submitted ? 'true' : 'false'}>
                <strong>{a.pet.name ?? ''}</strong> · <time dateTime={a.starts_at}>{when(a.starts_at)}</time> · {mode(a.mode)}
                <div>{t('owner')}: {a.owner_name ?? ''}{a.reason ? ` — ${a.reason}` : ''}</div>
                <small>{t(a.intake_submitted ? 'intake' : 'noIntake')}</small>
              </li>
            ))}</ol>
          )}
          <h2>{t('open')}</h2>
          {q.open_consultations.length === 0 ? <p data-testid="queue-no-open">{t('noOpen')}</p> : (
            <ol>{q.open_consultations.map(c => (
              <li key={c.session_id} data-testid="queue-open-consultation" data-session={c.session_id}>
                <strong>{c.pet.name ?? ''}</strong> · {when(c.created_at)} · {mode(c.mode)} · {t('owner')}: {c.owner_name ?? ''}
              </li>
            ))}</ol>
          )}
        </>
      )}
    </main>
  )
}
