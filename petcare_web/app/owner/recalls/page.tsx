'use client'

/**
 * FR-19 — the owner's recall notices (MVC-BUILD-RUNNER-001 U13).
 *
 * Ratified AC-FR-19-02: a recall of a product batch resolves through stored records to every affected
 * owner, and each affected owner is notified. This page shows the served notices for the signed-in
 * owner. Route: /owner/recalls. Arabic default, RTL.
 */

import { useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'

type Notice = { notification_id: string; recall_id: string; body: string; created_at: string }

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')

const L = {
  title: { ar: 'تنبيهات سحب المنتجات', en: 'Product recall notices' },
  none: { ar: 'لا توجد تنبيهات سحب تخص حيواناتك.', en: 'No recall notices concern your pets.' },
  intro: { ar: 'تم سحب تشغيلة من دواء صُرف لحيوانك الأليف. يرجى التواصل مع عيادتك.',
    en: 'A batch of a medicine dispensed for your pet has been recalled. Please contact your clinic.' },
  error: { ar: 'تعذر تحميل التنبيهات', en: 'Notices could not be loaded' },
} as const

export default function OwnerRecallsPage() {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  const t = (k: keyof typeof L) => L[k][isAr ? 'ar' : 'en']
  const [items, setItems] = useState<Notice[]>([])
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    void (async () => {
      try {
        const r = await fetch(`${apiBase}/api/me/recall-notices`, { credentials: 'include', cache: 'no-store' })
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
      {items.map(n => (
        <section key={n.notification_id} className="card stack" data-testid="recall-notice" role="alert">
          <strong>{t('intro')}</strong>
          <div dir="auto">{n.body}</div>
          <small>{new Date(n.created_at).toLocaleString(isAr ? 'ar-SA' : 'en-GB', { dateStyle: 'medium' })}</small>
        </section>
      ))}
    </main>
  )
}
