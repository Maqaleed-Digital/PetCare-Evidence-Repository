'use client'

/**
 * FR-07 — consultation messages and file sharing (MVC-BUILD-RUNNER-001 U7).
 *
 * Ratified AC-FR-07-01: owner and vet exchange messages and share files (images, lab
 * reports) within a consultation; nothing is visible outside it. The served API
 * enforces participation (404 outside the consultation); this page sends no actor,
 * owner or tenant — the session decides. Arabic default, RTL.
 * Route: /account/messages?consultation=<id>
 */

import { FormEvent, Suspense, useCallback, useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { useLang } from '@/components/LangProvider'

type Attachment = { attachment_id: string; filename: string; byte_size: number }
type Message = { message_id: string; sender_role: string; body: string; created_at: string; attachments: Attachment[] }

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
const call = (path: string, init?: RequestInit) =>
  fetch(`${apiBase}${path}`, { credentials: 'include', cache: 'no-store', ...init })

const L = {
  title: { ar: 'رسائل الاستشارة', en: 'Consultation messages' },
  empty: { ar: 'لا توجد رسائل بعد.', en: 'No messages yet.' },
  noConsultation: { ar: 'لم يتم تحديد استشارة.', en: 'No consultation selected.' },
  body: { ar: 'الرسالة', en: 'Message' },
  file: { ar: 'إرفاق صورة أو تقرير مختبر', en: 'Attach an image or lab report' },
  send: { ar: 'إرسال', en: 'Send' },
  download: { ar: 'تنزيل', en: 'Download' },
  error: { ar: 'تعذر إكمال الطلب', en: 'The request could not be completed' },
} as const

function Thread() {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  const t = (k: keyof typeof L) => L[k][isAr ? 'ar' : 'en']
  const consultation = useSearchParams().get('consultation') ?? ''
  const [messages, setMessages] = useState<Message[]>([])
  const [failed, setFailed] = useState(false)

  const load = useCallback(async () => {
    if (!consultation) return
    const r = await call(`/api/consultations/${consultation}/messages`)
    if (!r.ok) { setFailed(true); return }
    setMessages(await r.json())
  }, [consultation])

  useEffect(() => { void load() }, [load])

  async function send(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const form = e.currentTarget
    const f = new FormData(form)
    const body = String(f.get('body') ?? '').trim()
    if (!body) return
    const r = await call(`/api/consultations/${consultation}/messages`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ body }),
    })
    if (!r.ok) { setFailed(true); return }
    const file = (form.elements.namedItem('file') as HTMLInputElement | null)?.files?.[0]
    if (file && file.size > 0) {
      const m = await r.json()
      const up = new FormData()
      up.append('file', file)
      const a = await call(`/api/consultations/${consultation}/messages/${m.message_id}/attachments`,
        { method: 'POST', body: up })
      if (!a.ok) { setFailed(true) }
    }
    form.reset()
    await load()
  }

  if (!consultation) return <p>{t('noConsultation')}</p>
  return (
    <>
      {failed && <p role="alert">{t('error')}</p>}
      {messages.length === 0 ? <p>{t('empty')}</p> : (
        <ul aria-label={t('title')}>
          {messages.map(m => (
            <li key={m.message_id}>
              <p>{m.body}</p>
              {m.attachments.map(a => (
                <a key={a.attachment_id}
                   href={`${apiBase}/api/consultations/${consultation}/messages/${m.message_id}/attachments/${a.attachment_id}`}>
                  {t('download')} · {a.filename}
                </a>
              ))}
            </li>
          ))}
        </ul>
      )}
      <form onSubmit={e => void send(e)} aria-label={t('send')}>
        <label>{t('body')}<textarea name="body" required /></label>
        <label>{t('file')}<input name="file" type="file" accept="image/png,image/jpeg,image/heic,application/pdf" /></label>
        <button type="submit">{t('send')}</button>
      </form>
    </>
  )
}

export default function MessagesPage() {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  return (
    <main className="stack" dir={isAr ? 'rtl' : 'ltr'} lang={isAr ? 'ar' : 'en'}>
      <h1 className="title-lg">{L.title[isAr ? 'ar' : 'en']}</h1>
      <Suspense fallback={null}><Thread /></Suspense>
    </main>
  )
}
