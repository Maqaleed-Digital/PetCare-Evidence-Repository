'use client'

/**
 * FR-20 — checkout with cash on delivery, and digital receipts (MVC-BUILD-RUNNER-001 U14).
 *
 * AC-FR-20-01: the owner chooses cash on delivery at checkout; the served order records COD. Prices come
 * from the tenant's price list on the server — the page sends product and quantity only.
 * AC-FR-20-02: after delivery the owner reads the digital receipt, persisted against the order, in their
 * chosen language (Arabic by default, right-to-left). Route: /owner/orders.
 */

import { FormEvent, useCallback, useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'

type Priced = { product_id: string; unit_price_halalas: number }
type Receipt = { receipt_id: string; language: string; rendered: string; issued_at: string }
type Order = { order_id: string; payment_method: string; status: string; paid: boolean; total_halalas: number;
  receipt: Receipt | null }

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
const call = (path: string, init?: RequestInit) =>
  fetch(`${apiBase}${path}`, { credentials: 'include', cache: 'no-store', ...init })

const L = {
  title: { ar: 'طلباتي', en: 'My orders' },
  checkout: { ar: 'إتمام الطلب', en: 'Checkout' },
  quantity: { ar: 'الكمية', en: 'Quantity' },
  payment: { ar: 'طريقة الدفع', en: 'Payment method' },
  cod: { ar: 'الدفع عند الاستلام', en: 'Cash on delivery' },
  place: { ar: 'تأكيد الطلب', en: 'Place order' },
  none: { ar: 'لا توجد طلبات بعد.', en: 'No orders yet.' },
  receipt: { ar: 'الإيصال الرقمي', en: 'Digital receipt' },
  PLACED: { ar: 'بانتظار التوصيل', en: 'Awaiting delivery' },
  DELIVERED: { ar: 'تم التسليم والدفع', en: 'Delivered and paid' },
  sar: { ar: 'ر.س', en: 'SAR' },
  error: { ar: 'تعذر إتمام الطلب', en: 'The order could not be placed' },
} as const

export default function OwnerOrdersPage() {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  const t = (k: keyof typeof L) => L[k][isAr ? 'ar' : 'en']
  const [catalog, setCatalog] = useState<Priced[]>([])
  const [orders, setOrders] = useState<Order[]>([])
  const [qty, setQty] = useState<Record<string, number>>({})
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    const [c, o] = await Promise.all([call('/api/catalog/prices'), call('/api/orders')])
    if (c.ok) setCatalog(await c.json())
    if (o.ok) setOrders(await o.json())
  }, [])
  useEffect(() => { void load() }, [load])

  const money = (h: number) => `${(h / 100).toLocaleString(isAr ? 'ar-SA' : 'en-GB', { minimumFractionDigits: 2 })} ${t('sar')}`

  async function place(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const method = String(new FormData(e.currentTarget).get('payment_method') ?? '')
    const lines = Object.entries(qty).filter(([, q]) => q > 0).map(([product_id, quantity]) => ({ product_id, quantity }))
    if (!lines.length || !method) return
    const r = await call('/api/orders', { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lines, payment_method: method }) })
    setError(r.ok ? '' : t('error'))
    if (r.ok) { setQty({}); await load() }
  }

  return (
    <main className="stack" dir={isAr ? 'rtl' : 'ltr'}>
      <h1 className="title-lg">{t('title')}</h1>
      {catalog.length > 0 && (
        <form onSubmit={place} className="card stack" aria-label={t('checkout')}>
          <h2 className="title-md">{t('checkout')}</h2>
          {catalog.map(p => (
            <label key={p.product_id}>{p.product_id} · {money(p.unit_price_halalas)} · {t('quantity')}
              <input type="number" min={0} name={`qty-${p.product_id}`} value={qty[p.product_id] ?? 0}
                onChange={e => setQty({ ...qty, [p.product_id]: Number(e.target.value) })} />
            </label>
          ))}
          <fieldset>
            <legend>{t('payment')}</legend>
            <label><input type="radio" name="payment_method" value="COD" defaultChecked /> {t('cod')}</label>
          </fieldset>
          <button type="submit" className="btn">{t('place')}</button>
          {error && <p role="alert">{error}</p>}
        </form>
      )}
      {orders.length === 0 && <p className="muted">{t('none')}</p>}
      {orders.map(o => (
        <section key={o.order_id} className="card stack" data-testid="order">
          <div>{t(o.status === 'DELIVERED' ? 'DELIVERED' : 'PLACED')} · {t('cod')} · {money(o.total_halalas)}</div>
          {o.receipt && (
            <article data-testid="receipt" lang={o.receipt.language} dir={o.receipt.language === 'ar' ? 'rtl' : 'ltr'}>
              <h3>{t('receipt')}</h3>
              <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>{o.receipt.rendered}</pre>
            </article>
          )}
        </section>
      ))}
    </main>
  )
}
