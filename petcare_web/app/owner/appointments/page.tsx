'use client'

/**
 * CO-07 my appointments (MVC-EPC-D-001 Lane D, D2e — journey J-O5). The owner's bookings as the server holds them;
 * reschedule opens the booking screen for that booking, cancel asks for confirmation and then asks the server.
 */

import { useCallback, useEffect, useState } from 'react'
import { Button, Copy, DataView, Notice, Page, useCopy } from '@/components/ui'

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
const get = (path: string) => fetch(`${apiBase}${path}`, { credentials: 'include', cache: 'no-store' })
  .then(r => (r.ok ? r.json() : Promise.reject(r.status)))

const A = {
  kicker: { ar: 'بوابة المالك', en: 'Owner portal' },
  title: { ar: 'مواعيدي', en: 'My appointments' },
  empty: { ar: 'لا توجد مواعيد بعد.', en: 'No appointments yet.' },
  book: { ar: 'حجز استشارة', en: 'Book a consultation' },
  booked: { ar: 'محجوز', en: 'Booked' },
  cancelled: { ar: 'ملغى', en: 'Cancelled' },
  inClinic: { ar: 'في العيادة', en: 'In clinic' },
  video: { ar: 'مرئية', en: 'Video' },
  reschedule: { ar: 'تغيير الموعد', en: 'Reschedule' },
  cancel: { ar: 'إلغاء الموعد', en: 'Cancel appointment' },
  confirm: { ar: 'تأكيد الإلغاء', en: 'Confirm cancellation' },
  keep: { ar: 'إبقاء الموعد', en: 'Keep appointment' },
  failed: { ar: 'تعذّر إلغاء الموعد. حاول مرة أخرى.', en: 'The appointment could not be cancelled. Try again.' },
  with: { ar: 'مع', en: 'with' },
} satisfies Record<string, Copy>

type Booking = { booking_id: string; pet_id: string; veterinarian_id: string; mode: string; starts_at: string; status: string }

export default function AppointmentsPage() {
  const { tr, lang } = useCopy()
  const [status, setStatus] = useState<'loading' | 'error' | 'ready'>('loading')
  const [items, setItems] = useState<Booking[] | null>(null)
  const [pets, setPets] = useState<Record<string, string>>({})
  const [vets, setVets] = useState<Record<string, string>>({})
  const [confirming, setConfirming] = useState<string | null>(null)
  const [failed, setFailed] = useState(false)

  const load = useCallback(() => {
    setStatus('loading')
    Promise.all([get('/api/bookings'), get('/api/pets'), get('/api/booking/veterinarians')])
      .then(([b, p, v]: [Booking[], { pet_id: string; name: string }[], { user_id: string; full_name: string }[]]) => {
        setPets(Object.fromEntries(p.map(x => [x.pet_id, x.name])))
        setVets(Object.fromEntries(v.map(x => [x.user_id, x.full_name])))
        setItems(b); setStatus('ready')
      })
      .catch(() => setStatus('error'))
  }, [])
  useEffect(load, [load])

  const cancel = async (id: string) => {
    setFailed(false)
    const r = await fetch(`${apiBase}/api/bookings/${encodeURIComponent(id)}/cancel`, { method: 'POST', credentials: 'include' })
    setConfirming(null)
    if (!r.ok) { setFailed(true); return }
    load()
  }

  const when = (iso: string) => new Date(iso).toLocaleString(lang === 'ar' ? 'ar-SA' : 'en-GB',
    { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Riyadh' })

  return (
    <Page kicker={A.kicker} title={A.title} testId="appointments-page">
      <div className="ds-row"><a className="ds-btn" href="/owner/book" data-testid="appointments-book">{tr(A.book)}</a></div>
      {failed && <Notice tone="danger">{tr(A.failed)}</Notice>}
      <DataView status={status} data={items} onRetry={load} empty={A.empty}>
        {list => (
          <ol className="ds-list" aria-label={tr(A.title)}>
            {list.map(b => (
              <li key={b.booking_id} data-testid="appointment" data-status={b.status}>
                <div className="ds-row ds-row--between">
                  <strong>{pets[b.pet_id] ?? ''}</strong>
                  <span className={`ds-badge${b.status === 'BOOKED' ? ' ds-badge--success' : ''}`}>
                    {tr(b.status === 'BOOKED' ? A.booked : A.cancelled)}
                  </span>
                </div>
                <p className="ds-muted">
                  <time dateTime={b.starts_at}>{when(b.starts_at)}</time> · {tr(A.with)} {vets[b.veterinarian_id] ?? ''} ·{' '}
                  {tr(b.mode === 'VIDEO' ? A.video : A.inClinic)}
                </p>
                {b.status === 'BOOKED' && (
                  <div className="ds-row">
                    <a className="ds-link" data-testid="appointment-reschedule"
                      href={`/owner/book?reschedule=${encodeURIComponent(b.booking_id)}&vet=${encodeURIComponent(b.veterinarian_id)}`}>
                      {tr(A.reschedule)}
                    </a>
                    {confirming === b.booking_id ? (
                      <>
                        <Button variant="danger" onClick={() => cancel(b.booking_id)} data-testid="appointment-cancel-confirm">{tr(A.confirm)}</Button>
                        <Button variant="secondary" onClick={() => setConfirming(null)}>{tr(A.keep)}</Button>
                      </>
                    ) : (
                      <Button variant="secondary" onClick={() => setConfirming(b.booking_id)} data-testid="appointment-cancel">{tr(A.cancel)}</Button>
                    )}
                  </div>
                )}
              </li>
            ))}
          </ol>
        )}
      </DataView>
    </Page>
  )
}
