'use client'

/**
 * CO-09 messages (MVC-EPC-D-001 Lane D, D2f — journey J-O6; FR-07). The secure thread of one of the owner's
 * consultations: messages and shared files (images, lab reports) exchanged with the veterinarian. The served API decides
 * participation (404 outside the consultation); this screen sends only the message text and the file — never an actor,
 * owner or tenant. Route: /owner/consultations/messages?consultation=<id>.
 */

import { FormEvent, Suspense, useCallback, useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { Button, Copy, DataView, Notice, Page, useCopy } from '@/components/ui'

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
const call = (path: string, init?: RequestInit) => fetch(`${apiBase}${path}`, { credentials: 'include', cache: 'no-store', ...init })

const M = {
  kicker: { ar: 'استشاراتي', en: 'My consultations' },
  title: { ar: 'الرسائل والملفات', en: 'Messages and files' },
  back: { ar: 'العودة إلى استشاراتي', en: 'Back to my consultations' },
  empty: { ar: 'لا توجد رسائل بعد. اكتب رسالتك الأولى للطبيب البيطري.', en: 'No messages yet. Write your first message to the veterinarian.' },
  none: { ar: 'لم يتم تحديد استشارة.', en: 'No consultation selected.' },
  you: { ar: 'أنت', en: 'You' },
  vet: { ar: 'الطبيب البيطري', en: 'Veterinarian' },
  body: { ar: 'رسالتك', en: 'Your message' },
  file: { ar: 'إرفاق صورة أو تقرير (اختياري)', en: 'Attach an image or report (optional)' },
  fileHint: { ar: 'صورة أو تقرير بصيغة مستند محمول.', en: 'PNG, JPEG or HEIC images, or a PDF.' },
  send: { ar: 'إرسال', en: 'Send' },
  sending: { ar: 'جارٍ الإرسال…', en: 'Sending…' },
  download: { ar: 'تنزيل', en: 'Download' },
  sendFailed: { ar: 'تعذّر إرسال الرسالة. حاول مرة أخرى.', en: 'The message could not be sent. Try again.' },
  fileFailed: { ar: 'أُرسلت الرسالة لكن تعذّر إرفاق الملف. تحقّق من نوعه وحجمه.', en: 'The message was sent but the file could not be attached. Check its type and size.' },
} satisfies Record<string, Copy>

type Attachment = { attachment_id: string; filename: string; byte_size: number }
type Message = { message_id: string; sender_id: string; sender_role: string; body: string; created_at: string; attachments: Attachment[] }

function Thread() {
  const { tr, lang } = useCopy()
  const consultation = useSearchParams().get('consultation') ?? ''
  const [status, setStatus] = useState<'loading' | 'error' | 'ready'>('loading')
  const [messages, setMessages] = useState<Message[] | null>(null)
  const [problem, setProblem] = useState<Copy | null>(null)
  const [busy, setBusy] = useState(false)
  const base = `/api/consultations/${encodeURIComponent(consultation)}/messages`

  const load = useCallback(() => {
    if (!consultation) return
    setStatus('loading')
    call(base).then(r => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((m: Message[]) => { setMessages(m); setStatus('ready') })
      .catch(() => setStatus('error'))
  }, [base, consultation])
  useEffect(load, [load])

  async function send(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const form = e.currentTarget
    const body = String(new FormData(form).get('body') ?? '').trim()
    if (!body) return
    setBusy(true); setProblem(null)
    try {
      const r = await call(base, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ body }) })
      if (!r.ok) { setProblem(M.sendFailed); return }
      const file = (form.elements.namedItem('file') as HTMLInputElement | null)?.files?.[0]
      if (file && file.size > 0) {
        const sent = await r.json()
        const up = new FormData()
        up.append('file', file)
        const a = await call(`${base}/${encodeURIComponent(sent.message_id)}/attachments`, { method: 'POST', body: up })
        if (!a.ok) setProblem(M.fileFailed)
      }
      form.reset()
      load()
    } catch {
      setProblem(M.sendFailed)
    } finally {
      setBusy(false)
    }
  }

  if (!consultation) return <Notice tone="warn">{tr(M.none)}</Notice>
  const when = (iso: string) => new Date(iso).toLocaleString(lang === 'ar' ? 'ar-SA' : 'en-GB',
    { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Riyadh' })
  return (
    <>
      <DataView status={status} data={messages} onRetry={load} empty={M.empty}>
        {list => (
          <ol className="ds-list" aria-label={tr(M.title)} data-testid="message-thread">
            {list.map(m => (
              <li key={m.message_id} data-testid="message" data-sender-role={m.sender_role}>
                <div className="ds-row ds-row--between">
                  <strong>{tr(m.sender_role === 'owner' ? M.you : M.vet)}</strong>
                  <time className="ds-muted" dateTime={m.created_at}>{when(m.created_at)}</time>
                </div>
                <p data-testid="message-body">{m.body}</p>
                {m.attachments.map(a => (
                  <a key={a.attachment_id} className="ds-link" data-testid="message-attachment"
                     href={`${apiBase}${base}/${encodeURIComponent(m.message_id)}/attachments/${encodeURIComponent(a.attachment_id)}`}>
                    {tr(M.download)} · <bdi translate="no">{a.filename}</bdi>
                  </a>
                ))}
              </li>
            ))}
          </ol>
        )}
      </DataView>
      {problem && <Notice tone="danger" testId="message-problem">{tr(problem)}</Notice>}
      <form className="ds-stack" onSubmit={e => void send(e)} aria-label={tr(M.send)} data-testid="message-form">
        <label className="ds-field">
          <span className="ds-label">{tr(M.body)}</span>
          <textarea className="ds-input" name="body" required maxLength={4000} rows={3} />
        </label>
        <label className="ds-field">
          <span className="ds-label">{tr(M.file)}</span>
          <input className="ds-input" name="file" type="file" accept="image/png,image/jpeg,image/heic,application/pdf" data-testid="message-file" />
          <span className="ds-hint">{tr(M.fileHint)}</span>
        </label>
        <Button type="submit" disabled={busy} data-testid="message-send">{tr(busy ? M.sending : M.send)}</Button>
      </form>
    </>
  )
}

export default function OwnerConsultationMessagesPage() {
  const { tr } = useCopy()
  return (
    <Page kicker={M.kicker} title={M.title} testId="messages-page">
      <div className="ds-row"><a className="ds-link" href="/owner/consultations" data-testid="messages-back">{tr(M.back)}</a></div>
      <Suspense fallback={null}><Thread /></Suspense>
    </Page>
  )
}
