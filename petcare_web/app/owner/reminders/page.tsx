'use client'

/**
 * FR-23 — the owner's vaccination and treatment reminders (MVC-BUILD-RUNNER-001 U15).
 *
 * Ratified AC-FR-23-01: a recorded due date produces reminders 7 days before, and 24 hours before if still
 * outstanding. AC-FR-23-02: each reminder is written in the owner's chosen language (Arabic primary).
 * This page shows the served reminders. Route: /owner/reminders. Arabic default, RTL.
 */

import { useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'

type Reminder = { reminder_id: string; kind: string; language: string; body: string; sent_at: string }

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')

const L = {
  title: { ar: 'التذكيرات', en: 'Reminders' },
  none: { ar: 'لا توجد تذكيرات حالياً.', en: 'No reminders right now.' },
  REMIND_7D: { ar: 'قبل ٧ أيام', en: '7 days before' },
  REMIND_24H: { ar: 'قبل ٢٤ ساعة', en: '24 hours before' },
  error: { ar: 'تعذر تحميل التذكيرات', en: 'Reminders could not be loaded' },
} as const

export default function OwnerRemindersPage() {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  const t = (k: keyof typeof L) => L[k][isAr ? 'ar' : 'en']
  const [items, setItems] = useState<Reminder[]>([])
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    void (async () => {
      try {
        const r = await fetch(`${apiBase}/api/me/reminders`, { credentials: 'include', cache: 'no-store' })
        if (!r.ok) { setFailed(true); return }
        setItems(await r.json())
      } catch { setFailed(true) }
    })()
  }, [])

  return (
    <main className="stack" dir={isAr ? 'rtl' : 'ltr'}>
      <h1 className="title-lg">{t('title')}</h1>
      {failed && <p role="alert">{t('error')}</p>}
      {!failed && items.length === 0 && <p className="muted">{t('none')}</p>}
      {items.map(r => (
        <section key={r.reminder_id} className="card" data-testid="reminder" lang={r.language}
          dir={r.language === 'ar' ? 'rtl' : 'ltr'}>
          <small>{r.kind === 'REMIND_24H' ? t('REMIND_24H') : t('REMIND_7D')}</small>
          <p>{r.body}</p>
        </section>
      ))}
    </main>
  )
}
