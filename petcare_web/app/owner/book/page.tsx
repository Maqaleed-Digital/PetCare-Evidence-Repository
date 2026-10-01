'use client'

/**
 * CO-05 book a consultation (MVC-EPC-D-001 Lane D, D2e — journey J-O5). The owner picks one of their own pets, a
 * veterinarian of their clinic, a day and a free slot served by the API; the server decides everything else (owner,
 * clinic, whether the slot is still free). `?reschedule=<booking id>&vet=<id>` moves an existing booking instead.
 * Video consultations stay behind their switch (SQ-2), so only in-clinic is offered here.
 */

import { useCallback, useEffect, useState } from 'react'
import { Button, Copy, DataView, Notice, Page, useCopy } from '@/components/ui'

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
const get = (path: string) => fetch(`${apiBase}${path}`, { credentials: 'include', cache: 'no-store' })
  .then(r => (r.ok ? r.json() : Promise.reject(r.status)))
const post = (path: string, body: unknown) => fetch(`${apiBase}${path}`, {
  method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
})

const B = {
  kicker: { ar: 'بوابة المالك', en: 'Owner portal' },
  title: { ar: 'حجز استشارة', en: 'Book a consultation' },
  titleMove: { ar: 'تغيير موعد الاستشارة', en: 'Reschedule a consultation' },
  pet: { ar: 'الحيوان', en: 'Pet' },
  vet: { ar: 'الطبيب البيطري', en: 'Veterinarian' },
  day: { ar: 'اليوم', en: 'Day' },
  slots: { ar: 'المواعيد المتاحة', en: 'Available times' },
  noSlots: { ar: 'لا توجد مواعيد متاحة في هذا اليوم.', en: 'No times are available on this day.' },
  noPets: { ar: 'أضف حيوانك أولاً من صفحة الحيوانات.', en: 'Add your pet first on the pets page.' },
  noVets: { ar: 'لا يوجد طبيب بيطري متاح في عيادتك حالياً.', en: 'No veterinarian is available at your clinic yet.' },
  mode: { ar: 'نوع الزيارة', en: 'Visit type' },
  inClinic: { ar: 'في العيادة', en: 'In clinic' },
  videoOff: { ar: 'الاستشارة المرئية غير مفعّلة بعد.', en: 'Video consultations are not switched on yet.' },
  reason: { ar: 'سبب الزيارة (اختياري)', en: 'Reason for the visit (optional)' },
  submit: { ar: 'تأكيد الحجز', en: 'Confirm booking' },
  submitMove: { ar: 'تأكيد الموعد الجديد', en: 'Confirm new time' },
  taken: { ar: 'تم حجز هذا الموعد للتو. اختر موعداً آخر.', en: 'That time was just taken. Choose another.' },
  failed: { ar: 'تعذّر الحجز. حاول مرة أخرى.', en: 'The booking could not be made. Try again.' },
  pickSlot: { ar: 'اختر موعداً.', en: 'Choose a time.' },
  mine: { ar: 'مواعيدي', en: 'My appointments' },
} satisfies Record<string, Copy>

type Pet = { pet_id: string; name: string; species: string }
type Vet = { user_id: string; full_name: string }

const clinicDay = (offset: number) => {
  const d = new Date(Date.now() + offset * 86_400_000)
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Riyadh' }).format(d)   // YYYY-MM-DD in clinic time
}

export default function BookPage() {
  const { tr, lang } = useCopy()
  const [status, setStatus] = useState<'loading' | 'error' | 'ready'>('loading')
  const [pets, setPets] = useState<Pet[]>([])
  const [vets, setVets] = useState<Vet[]>([])
  const [moving, setMoving] = useState<{ id: string; vet: string } | null>(null)
  const [pet, setPet] = useState('')
  const [vet, setVet] = useState('')
  const [day, setDay] = useState(clinicDay(1))
  const [slots, setSlots] = useState<string[] | 'loading' | 'error'>('loading')
  const [slot, setSlot] = useState('')
  const [reason, setReason] = useState('')
  const [problem, setProblem] = useState<Copy | null>(null)
  const [busy, setBusy] = useState(false)

  const load = useCallback(() => {
    setStatus('loading')
    const q = new URLSearchParams(window.location.search)
    const id = q.get('reschedule'); const v = q.get('vet')
    if (id && v) { setMoving({ id, vet: v }); setVet(v) }
    Promise.all([get('/api/pets'), get('/api/booking/veterinarians')])
      .then(([p, vs]: [Pet[], Vet[]]) => {
        setPets(p); setVets(vs)
        setPet(prev => prev || p[0]?.pet_id || '')
        setVet(prev => prev || vs[0]?.user_id || '')
        setStatus('ready')
      })
      .catch(() => setStatus('error'))
  }, [])
  useEffect(load, [load])

  useEffect(() => {
    if (!vet || !day) return
    setSlots('loading'); setSlot('')
    get(`/api/booking/slots?veterinarian_id=${encodeURIComponent(vet)}&day=${encodeURIComponent(day)}`)
      .then((s: string[]) => setSlots(s))
      .catch(() => setSlots('error'))
  }, [vet, day])

  const time = (iso: string) => new Date(iso).toLocaleTimeString(lang === 'ar' ? 'ar-SA' : 'en-GB',
    { hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Riyadh' })

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!slot) { setProblem(B.pickSlot); return }
    setBusy(true); setProblem(null)
    const r = moving
      ? await post(`/api/bookings/${encodeURIComponent(moving.id)}/reschedule`, { starts_at: slot })
      : await post('/api/bookings', { pet_id: pet, veterinarian_id: vet, starts_at: slot, mode: 'IN_CLINIC', reason })
    setBusy(false)
    if (r.ok) { window.location.assign('/owner/appointments'); return }
    const body = await r.json().catch(() => ({}))
    if (body?.detail?.error === 'SLOT_TAKEN') {
      setProblem(B.taken)
      setSlots(prev => (Array.isArray(prev) ? prev.filter(s => s !== slot) : prev)); setSlot('')
    } else setProblem(B.failed)
  }

  return (
    <Page kicker={B.kicker} title={moving ? B.titleMove : B.title} testId="book-page">
      <DataView status={status} data={pets} onRetry={load} empty={B.noPets}>
        {list => vets.length === 0 ? <Notice tone="warn">{tr(B.noVets)}</Notice> : (
          <form className="ds-stack" onSubmit={submit} data-testid="book-form">
            {!moving && (
              <div className="ds-field">
                <label className="ds-label" htmlFor="book-pet">{tr(B.pet)}</label>
                <select id="book-pet" name="pet" className="ds-input" value={pet} onChange={e => setPet(e.target.value)}>
                  {list.map(p => <option key={p.pet_id} value={p.pet_id}>{p.name} · {p.species}</option>)}
                </select>
              </div>
            )}
            <div className="ds-field">
              <label className="ds-label" htmlFor="book-vet">{tr(B.vet)}</label>
              <select id="book-vet" name="vet" className="ds-input" value={vet} disabled={!!moving}
                onChange={e => setVet(e.target.value)}>
                {vets.map(v => <option key={v.user_id} value={v.user_id}>{v.full_name}</option>)}
              </select>
            </div>
            <div className="ds-field">
              <label className="ds-label" htmlFor="book-day">{tr(B.day)}</label>
              <input id="book-day" name="day" type="date" className="ds-input" value={day} min={clinicDay(0)}
                max={clinicDay(14)} onChange={e => setDay(e.target.value)} />
            </div>
            <fieldset className="ds-field" data-testid="book-slots">
              <legend className="ds-label">{tr(B.slots)}</legend>
              {slots === 'loading' && <DataView status="loading" data={null}>{() => null}</DataView>}
              {slots === 'error' && <DataView status="error" data={null} onRetry={() => setDay(d => d)}>{() => null}</DataView>}
              {Array.isArray(slots) && (slots.length === 0 ? <p className="ds-hint">{tr(B.noSlots)}</p> : (
                <div className="ds-row" role="radiogroup" aria-label={tr(B.slots)}>
                  {slots.map(s => (
                    <label key={s} className={`ds-chip${slot === s ? ' ds-chip--selected' : ''}`}>
                      <input type="radio" name="slot" value={s} checked={slot === s} onChange={() => setSlot(s)} />
                      <time dateTime={s}>{time(s)}</time>
                    </label>
                  ))}
                </div>
              ))}
            </fieldset>
            {!moving && (
              <>
                <fieldset className="ds-field">
                  <legend className="ds-label">{tr(B.mode)}</legend>
                  <label><input type="radio" name="mode" value="IN_CLINIC" checked readOnly /> {tr(B.inClinic)}</label>
                  <p className="ds-hint">{tr(B.videoOff)}</p>
                </fieldset>
                <div className="ds-field">
                  <label className="ds-label" htmlFor="book-reason">{tr(B.reason)}</label>
                  <textarea id="book-reason" name="reason" className="ds-input" maxLength={500} value={reason}
                    onChange={e => setReason(e.target.value)} />
                </div>
              </>
            )}
            {problem && <Notice tone="danger" testId="book-problem">{tr(problem)}</Notice>}
            <div className="ds-row">
              <Button type="submit" disabled={busy} data-testid="book-submit">{tr(moving ? B.submitMove : B.submit)}</Button>
              <a className="ds-link" href="/owner/appointments">{tr(B.mine)}</a>
            </div>
          </form>
        )}
      </DataView>
    </Page>
  )
}
