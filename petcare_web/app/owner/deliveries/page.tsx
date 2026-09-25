'use client'

/**
 * FR-16 — the owner's deliveries and their temperature logs (MVC-BUILD-RUNNER-001 U12).
 *
 * Ratified AC-FR-16-01: a delivery of a temperature-controlled product carries a temperature log that
 * the owner can see in the app (Journey 1 P272). The log comes from the served, durable record;
 * out-of-range readings are shown, never hidden. Route: /owner/deliveries. Arabic default, RTL.
 */

import { useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'

type Reading = { recorded_at: string; celsius: number; out_of_range: boolean }
type Delivery = { delivery_id: string; product_id: string; cold_chain: boolean; temp_min_c: number | null;
  temp_max_c: number | null; status: string; temperature_log: Reading[] }

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')

const L = {
  title: { ar: 'توصيلاتي', en: 'My deliveries' },
  none: { ar: 'لا توجد توصيلات.', en: 'No deliveries.' },
  coldChain: { ar: 'منتج يتطلب التبريد', en: 'Temperature-controlled product' },
  range: { ar: 'النطاق المسموح', en: 'Allowed range' },
  log: { ar: 'سجل درجات الحرارة', en: 'Temperature log' },
  empty: { ar: 'لا توجد قراءات بعد.', en: 'No readings yet.' },
  outOfRange: { ar: 'خارج النطاق', en: 'Out of range' },
  IN_TRANSIT: { ar: 'قيد التوصيل', en: 'In transit' },
  DELIVERED: { ar: 'تم التسليم', en: 'Delivered' },
  error: { ar: 'تعذر تحميل التوصيلات', en: 'Deliveries could not be loaded' },
} as const

export default function OwnerDeliveriesPage() {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  const t = (k: keyof typeof L) => L[k][isAr ? 'ar' : 'en']
  const [items, setItems] = useState<Delivery[]>([])
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    void (async () => {
      try {
        const r = await fetch(`${apiBase}/api/deliveries`, { credentials: 'include', cache: 'no-store' })
        if (!r.ok) { setFailed(true); return }
        setItems(await r.json())
      } catch { setFailed(true) }
    })()
  }, [])

  const when = (iso: string) => new Date(iso).toLocaleString(isAr ? 'ar-SA' : 'en-GB', { dateStyle: 'short', timeStyle: 'short' })
  const deg = (n: number) => n.toLocaleString(isAr ? 'ar-SA' : 'en-GB')

  return (
    <main className="stack" dir={isAr ? 'rtl' : 'ltr'}>
      <h1 className="title-lg">{t('title')}</h1>
      {failed && <p role="alert">{t('error')}</p>}
      {!failed && items.length === 0 && <p className="muted">{t('none')}</p>}
      {items.map(d => (
        <section key={d.delivery_id} className="card stack" data-testid="delivery">
          <div>{t(d.status === 'DELIVERED' ? 'DELIVERED' : 'IN_TRANSIT')}</div>
          {d.cold_chain && (
            <>
              <div>{t('coldChain')} · {t('range')}: {deg(d.temp_min_c ?? 0)}–{deg(d.temp_max_c ?? 0)}°</div>
              <h2 className="title-md">{t('log')}</h2>
              {d.temperature_log.length === 0 ? <p className="muted">{t('empty')}</p> : (
                <ul>
                  {d.temperature_log.map(r => (
                    <li key={r.recorded_at} data-testid="reading" data-out-of-range={r.out_of_range}>
                      {when(r.recorded_at)} · {deg(r.celsius)}°{r.out_of_range ? ` · ${t('outOfRange')}` : ''}
                    </li>
                  ))}
                </ul>
              )}
            </>
          )}
        </section>
      ))}
    </main>
  )
}
