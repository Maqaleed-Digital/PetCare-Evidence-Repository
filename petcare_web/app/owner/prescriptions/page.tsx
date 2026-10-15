'use client'

/**
 * CO-11 prescriptions + upload (MVC-EPC-D-001 Lane D, D2g — journey J-O7; FR-14 owner part). The prescriptions issued for
 * the owner's own pets and the prescriptions they uploaded from elsewhere, as the server holds them; an upload waits for a
 * veterinarian of the clinic to verify it. Only the pet selector, the file and an optional note leave the browser — never
 * an owner, tenant or actor. Each prescription links to its pet's profile and health timeline (CO-03).
 */

import { FormEvent, useCallback, useEffect, useState } from 'react'
import { Button, Copy, DataView, Notice, Page, useCopy } from '@/components/ui'
import { formatKsa } from '@/lib/ksaTime'

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
const get = (path: string) => fetch(`${apiBase}${path}`, { credentials: 'include', cache: 'no-store' })
  .then(r => (r.ok ? r.json() : Promise.reject(r.status)))

const P = {
  kicker: { ar: 'بوابة المالك', en: 'Owner portal' },
  title: { ar: 'الوصفات الطبية', en: 'Prescriptions' },
  issued: { ar: 'الوصفات الصادرة لحيواناتك', en: 'Prescriptions issued for your pets' },
  noIssued: { ar: 'لا توجد وصفات صادرة بعد.', en: 'No prescriptions issued yet.' },
  uploads: { ar: 'وصفات رفعتها للتحقق', en: 'Prescriptions you uploaded for verification' },
  noUploads: { ar: 'لم ترفع أي وصفة بعد.', en: 'You have not uploaded a prescription yet.' },
  ISSUED: { ar: 'صادرة', en: 'Issued' },
  VET_VERIFIED: { ar: 'تحقق منها الطبيب', en: 'Verified by the veterinarian' },
  DISPENSED: { ar: 'صُرفت', en: 'Dispensed' },
  AWAITING_VERIFICATION: { ar: 'بانتظار تحقق الطبيب البيطري', en: 'Awaiting the veterinarian’s verification' },
  timeline: { ar: 'الملف الصحي', en: 'Health timeline' },
  uploadTitle: { ar: 'رفع وصفة من عيادة أخرى', en: 'Upload a prescription from another clinic' },
  pet: { ar: 'الحيوان الأليف', en: 'Pet' },
  file: { ar: 'صورة الوصفة أو ملفها', en: 'Prescription photo or file' },
  fileHint: { ar: 'صورة أو مستند محمول.', en: 'A photo (PNG, JPEG, HEIC) or a PDF.' },
  note: { ar: 'ملاحظة (اختياري)', en: 'Note (optional)' },
  submit: { ar: 'رفع للتحقق', en: 'Upload for verification' },
  sending: { ar: 'جارٍ الرفع…', en: 'Uploading…' },
  noPets: { ar: 'أضف حيوانك الأليف أولاً لرفع وصفة له.', en: 'Add your pet first to upload a prescription for it.' },
  failed: { ar: 'تعذّر رفع الوصفة. تحقّق من نوع الملف وحجمه ثم حاول مرة أخرى.', en: 'The prescription could not be uploaded. Check the file type and size and try again.' },
  done: { ar: 'تم رفع الوصفة وهي بانتظار التحقق.', en: 'The prescription was uploaded and is awaiting verification.' },
} satisfies Record<string, Copy>

type Rx = { prescription_id: string; pet_id: string; medication_name: string; dosage: string; instructions: string; status: string; issued_at: string }
type Upload = { upload_id: string; pet_id: string; filename: string; note: string; status: string; uploaded_at: string }
type Body = { prescriptions: Rx[]; uploads: Upload[] }

export default function OwnerPrescriptionsPage() {
  const { tr, lang } = useCopy()
  const [status, setStatus] = useState<'loading' | 'error' | 'ready'>('loading')
  const [body, setBody] = useState<Body | null>(null)
  const [pets, setPets] = useState<{ pet_id: string; name: string }[]>([])
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState<'done' | 'failed' | null>(null)

  const load = useCallback(() => {
    setStatus('loading')
    Promise.all([get('/api/owner/prescriptions'), get('/api/pets')])
      .then(([b, p]: [Body, { pet_id: string; name: string }[]]) => { setBody(b); setPets(p); setStatus('ready') })
      .catch(() => setStatus('error'))
  }, [])
  useEffect(load, [load])

  const name = (id: string) => pets.find(p => p.pet_id === id)?.name ?? ''
  const label = (k: string) => (k in P ? tr(P[k as keyof typeof P]) : k)
  const when = (iso: string) => formatKsa(iso, lang, { year: 'numeric', month: 'long', day: 'numeric' })

  async function upload(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const form = e.currentTarget
    const file = (form.elements.namedItem('file') as HTMLInputElement | null)?.files?.[0]
    if (!file || file.size === 0) return
    const data = new FormData()                                   // exactly the pet selector, the note and the file
    data.append('pet_id', (form.elements.namedItem('pet_id') as HTMLSelectElement).value)
    data.append('note', (form.elements.namedItem('note') as HTMLTextAreaElement).value)
    data.append('file', file)
    setBusy(true); setResult(null)
    try {
      const r = await fetch(`${apiBase}/api/owner/prescriptions/uploads`, { method: 'POST', credentials: 'include', body: data })
      setResult(r.ok ? 'done' : 'failed')
      if (r.ok) { form.reset(); load() }
    } catch { setResult('failed') } finally { setBusy(false) }
  }

  return (
    <Page kicker={P.kicker} title={P.title} testId="prescriptions-page">
      <DataView status={status} data={body} onRetry={load}>
        {b => (
          <>
            <section className="ds-stack" aria-labelledby="rx-issued">
              <h2 id="rx-issued" className="title">{tr(P.issued)}</h2>
              {b.prescriptions.length === 0 ? <p className="ds-muted">{tr(P.noIssued)}</p> : (
                <ol className="ds-list">
                  {b.prescriptions.map(rx => (
                    <li key={rx.prescription_id} data-testid="owner-prescription" data-status={rx.status}>
                      <div className="ds-row ds-row--between">
                        <strong>{rx.medication_name} · <bdi translate="no">{rx.dosage}</bdi></strong>
                        <span className="ds-badge">{label(rx.status)}</span>
                      </div>
                      <p>{rx.instructions}</p>
                      <p className="ds-muted">
                        {name(rx.pet_id)} · <time dateTime={rx.issued_at}>{when(rx.issued_at)}</time> ·{' '}
                        <a className="ds-link" href="/owner/pets" data-testid="prescription-timeline">{tr(P.timeline)}</a>
                      </p>
                    </li>
                  ))}
                </ol>
              )}
            </section>
            <section className="ds-stack" aria-labelledby="rx-uploads">
              <h2 id="rx-uploads" className="title">{tr(P.uploads)}</h2>
              {b.uploads.length === 0 ? <p className="ds-muted">{tr(P.noUploads)}</p> : (
                <ol className="ds-list">
                  {b.uploads.map(u => (
                    <li key={u.upload_id} data-testid="owner-upload" data-status={u.status}>
                      <div className="ds-row ds-row--between">
                        <strong>{name(u.pet_id)}</strong>
                        <span className="ds-badge">{label(u.status)}</span>
                      </div>
                      <p className="ds-muted">
                        <bdi translate="no">{u.filename}</bdi> · <time dateTime={u.uploaded_at}>{when(u.uploaded_at)}</time>
                      </p>
                      {u.note && <p>{u.note}</p>}
                      <a className="ds-link" data-testid="owner-upload-download"
                         href={`${apiBase}/api/owner/prescriptions/uploads/${encodeURIComponent(u.upload_id)}/document`}>{tr(P.file)}</a>
                    </li>
                  ))}
                </ol>
              )}
            </section>
          </>
        )}
      </DataView>
      <section className="ds-stack" aria-labelledby="rx-upload">
        <h2 id="rx-upload" className="title">{tr(P.uploadTitle)}</h2>
        {status === 'ready' && pets.length === 0 ? <Notice tone="warn">{tr(P.noPets)}</Notice> : (
          <form className="ds-stack" onSubmit={e => void upload(e)} data-testid="upload-form" aria-label={tr(P.uploadTitle)}>
            <label className="ds-field">
              <span className="ds-label">{tr(P.pet)}</span>
              <select className="ds-input" name="pet_id" required>
                {pets.map(p => <option key={p.pet_id} value={p.pet_id}>{p.name}</option>)}
              </select>
            </label>
            <label className="ds-field">
              <span className="ds-label">{tr(P.file)}</span>
              <input className="ds-input" name="file" type="file" required accept="image/png,image/jpeg,image/heic,application/pdf" data-testid="upload-file" />
              <span className="ds-hint">{tr(P.fileHint)}</span>
            </label>
            <label className="ds-field">
              <span className="ds-label">{tr(P.note)}</span>
              <textarea className="ds-input" name="note" maxLength={500} rows={2} />
            </label>
            <Button type="submit" disabled={busy} data-testid="upload-submit">{tr(busy ? P.sending : P.submit)}</Button>
          </form>
        )}
        {result === 'done' && <Notice tone="success" testId="upload-done">{tr(P.done)}</Notice>}
        {result === 'failed' && <Notice tone="danger" testId="upload-failed">{tr(P.failed)}</Notice>}
      </section>
    </Page>
  )
}
