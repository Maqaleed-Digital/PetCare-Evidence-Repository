'use client'

/**
 * Owner consultations (MVC-EPC-D-001 Lane D, D2f — journey J-O6, entry to CO-09 messages and CO-08 video room). The
 * owner's consultations as the server holds them (GET /api/consultations returns only the caller's own); each opens its
 * secure message thread, and a video consultation opens its waiting room. Whether remote consultation is offered at all
 * comes from the server (AC-FR-06-05, COUNSEL:REG-02) — this screen never decides it.
 */

import { useCallback, useEffect, useState } from 'react'
import { Copy, DataView, Notice, Page, useCopy } from '@/components/ui'

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
const get = (path: string) => fetch(`${apiBase}${path}`, { credentials: 'include', cache: 'no-store' })
  .then(r => (r.ok ? r.json() : Promise.reject(r.status)))

const C = {
  kicker: { ar: 'بوابة المالك', en: 'Owner portal' },
  title: { ar: 'استشاراتي', en: 'My consultations' },
  empty: { ar: 'لا توجد استشارات بعد. يبدأ الطبيب البيطري الاستشارة لحيوانك الأليف.', en: 'No consultations yet. Your veterinarian starts a consultation for your pet.' },
  remoteOff: { ar: 'الاستشارة المرئية غير متاحة حالياً إلى حين صدور الرأي القانوني المعتمد بشأن الطب البيطري عن بُعد.', en: 'Video consultation is not offered until the telemedicine counsel determination is recorded.' },
  inPerson: { ar: 'حضورية', en: 'In person' },
  video: { ar: 'مرئية', en: 'Video' },
  requested: { ar: 'مطلوبة', en: 'Requested' },
  completed: { ar: 'مكتملة', en: 'Completed' },
  messages: { ar: 'الرسائل والملفات', en: 'Messages and files' },
  room: { ar: 'غرفة الانتظار المرئية', en: 'Video waiting room' },
} satisfies Record<string, Copy>

type Consultation = { session_id: string; pet_id: string; mode: string; status: string; created_at: string }
type Body = { remote: { offered: boolean }; consultations: Consultation[] }

export default function OwnerConsultationsPage() {
  const { tr, lang } = useCopy()
  const [status, setStatus] = useState<'loading' | 'error' | 'ready'>('loading')
  const [body, setBody] = useState<Body | null>(null)
  const [pets, setPets] = useState<Record<string, string>>({})

  const load = useCallback(() => {
    setStatus('loading')
    Promise.all([get('/api/consultations'), get('/api/pets')])
      .then(([c, p]: [Body, { pet_id: string; name: string }[]]) => {
        setPets(Object.fromEntries(p.map(x => [x.pet_id, x.name])))
        setBody(c); setStatus('ready')
      })
      .catch(() => setStatus('error'))
  }, [])
  useEffect(load, [load])

  const when = (iso: string) => new Date(iso).toLocaleString(lang === 'ar' ? 'ar-SA' : 'en-GB',
    { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Riyadh' })

  return (
    <Page kicker={C.kicker} title={C.title} testId="consultations-page">
      {body && !body.remote.offered && <Notice testId="consultations-remote-off">{tr(C.remoteOff)}</Notice>}
      <DataView status={status} data={body ? body.consultations : null} onRetry={load} empty={C.empty}>
        {list => (
          <ol className="ds-list" aria-label={tr(C.title)}>
            {list.map(c => {
              const q = `consultation=${encodeURIComponent(c.session_id)}`
              return (
                <li key={c.session_id} data-testid="owner-consultation" data-mode={c.mode} data-status={c.status}>
                  <div className="ds-row ds-row--between">
                    <strong>{pets[c.pet_id] ?? ''}</strong>
                    <span className="ds-badge">{tr(c.status === 'COMPLETED' ? C.completed : C.requested)}</span>
                  </div>
                  <p className="ds-muted">
                    <time dateTime={c.created_at}>{when(c.created_at)}</time> · {tr(c.mode === 'REMOTE_VIDEO' ? C.video : C.inPerson)}
                  </p>
                  <div className="ds-row">
                    <a className="ds-link" href={`/owner/consultations/messages?${q}`} data-testid="consultation-open-messages">{tr(C.messages)}</a>
                    {c.mode === 'REMOTE_VIDEO' && (
                      <a className="ds-link" href={`/owner/consultations/video?${q}`} data-testid="consultation-open-video">{tr(C.room)}</a>
                    )}
                  </div>
                </li>
              )
            })}
          </ol>
        )}
      </DataView>
    </Page>
  )
}
