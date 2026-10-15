'use client'

/**
 * FR-20 — checkout with cash on delivery, and digital receipts (MVC-BUILD-RUNNER-001 U14).
 *
 * AC-FR-20-01: the owner chooses cash on delivery at checkout; the served order records COD. Prices come
 * from the tenant's price list on the server — the page sends product and quantity only.
 * AC-FR-20-02: after delivery the owner reads the digital receipt, persisted against the order, in their
 * chosen language (Arabic by default, right-to-left). Route: /owner/orders.
 *
 * J-O8 cash on delivery (MVC-EPC-D-001 D2m, R19.5 item 3): products are shown by their registered name; each order carries its
 * status for the journey; machine values (product names, ids, references) are marked translate="no" so the Arabic page holds
 * no untranslated copy. Online payment is not offered: it is blocked on X-05 / HyperPay (R18.4), never simulated.
 *
 * J-O9 internal tracking (D2n, R19.5 item 4): each order shows its own lifecycle — placed, pharmacy assigned, delivered, receipt
 * issued — from the platform's records (`tracking` on the order). There is no courier/carrier tracking (no logistics partner,
 * R18.4): the page says so and never shows a carrier status or ETA.
 */

import { FormEvent, useCallback, useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'
import { formatKsa } from '@/lib/ksaTime'

type Priced = { product_id: string; name?: string | null; unit_price_halalas: number }
type Line = { product_id: string; name?: string | null; quantity: number; unit_price_halalas: number }
type Receipt = { receipt_id: string; language: string; rendered: string; issued_at: string }
type Step = { step: 'PLACED' | 'ROUTED' | 'DELIVERED' | 'RECEIPT_ISSUED'; done: boolean; at: string | null }
type Order = { order_id: string; payment_method: string; status: string; paid: boolean; total_halalas: number;
  receipt: Receipt | null; fulfilled_by?: { location_id: string; name: string } | null; lines?: Line[];
  tracking?: { steps: Step[]; carrier: null } }

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
  fulfilledBy: { ar: 'تُنفَّذ من صيدلية', en: 'Fulfilled by pharmacy' },
  PLACED: { ar: 'بانتظار التوصيل', en: 'Awaiting delivery' },
  DELIVERED: { ar: 'تم التسليم والدفع', en: 'Delivered and paid' },
  sar: { ar: 'ر.س', en: 'SAR' },
  tracking: { ar: 'تتبّع الطلب', en: 'Order tracking' },
  step_PLACED: { ar: 'استُلم الطلب', en: 'Order placed' },
  step_ROUTED: { ar: 'حُدِّدت الصيدلية', en: 'Pharmacy assigned' },
  step_DELIVERED: { ar: 'سُلِّم الطلب', en: 'Delivered' },
  step_RECEIPT_ISSUED: { ar: 'صدر الإيصال', en: 'Receipt issued' },
  pending: { ar: 'لم يتم بعد', en: 'Not yet' },
  noCarrier: { ar: 'لا يتوفر تتبّع لدى شركة شحن؛ تُعرض الحالة من سجلات المنصة فقط.',
    en: "No courier tracking is available; the status comes from the platform's own records only." },
  error: { ar: 'تعذر إتمام الطلب', en: 'The order could not be placed' },
  // FR-04 AC-FR-04-01 (U17): the purchaser is told, in the purchase flow, that verification is required and why.
  restricted: { ar: 'الأدوية المقيّدة والخاضعة للرقابة غير متاحة للشراء عبر التطبيق: يتطلب شراؤها التحقق من هوية المشتري، '
    + 'وسير عملها معطّل إلى حين صدور الرأي القانوني المعتمد',
    en: 'Restricted and controlled medicines cannot be bought in the app: their purchase requires verification of the '
    + "purchaser's identity, and the workflow is disabled until counsel's determination is recorded" },
} as const

/** Machine values inside a server-rendered Arabic receipt (order id, product id, collection reference, ISO date) are copied
 *  verbatim, never translated: each Latin/digit token is set apart as translate="no". */
function Verbatim({ text }: { text: string }) {
  return <>{text.split(/([A-Za-z0-9][A-Za-z0-9._:/-]*)/).map((part, i) =>
    i % 2 ? <bdi key={i} translate="no">{part}</bdi> : part)}</>
}

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
      <p role="note" data-testid="restricted-notice">{t('restricted')} (<bdi translate="no">EV-11</bdi>).</p>
      {catalog.length > 0 && (
        <form onSubmit={place} className="card stack" aria-label={t('checkout')}>
          <h2 className="title-md">{t('checkout')}</h2>
          {catalog.map(p => (
            <label key={p.product_id} data-testid="catalog-item" data-product-id={p.product_id}>
              <bdi translate="no">{p.name ?? p.product_id}</bdi> · {money(p.unit_price_halalas)} · {t('quantity')}
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
        <section key={o.order_id} className="card stack" data-testid="order" data-status={o.status} data-order-id={o.order_id}>
          <div>{t(o.status === 'DELIVERED' ? 'DELIVERED' : 'PLACED')} · {t('cod')} · {money(o.total_halalas)}</div>
          {o.lines && o.lines.length > 0 && (
            <ul data-testid="order-lines">
              {o.lines.map(l => <li key={l.product_id}><bdi translate="no">{l.name ?? l.product_id}</bdi> × {l.quantity}</li>)}
            </ul>
          )}
          {o.tracking && (
            <section data-testid="order-tracking" aria-label={t('tracking')}>
              <h3 className="title-md">{t('tracking')}</h3>
              <ol>
                {o.tracking.steps.map(s => (
                  <li key={s.step} data-testid="tracking-step" data-step={s.step} data-done={s.done ? 'true' : 'false'}>
                    {t(`step_${s.step}` as keyof typeof L)} · {s.done && s.at
                      ? formatKsa(s.at, lang, { dateStyle: 'medium', timeStyle: 'short' }) : t('pending')}
                  </li>
                ))}
              </ol>
              <p className="muted" data-testid="tracking-no-carrier">{t('noCarrier')}</p>
            </section>
          )}
          {o.fulfilled_by && <div data-testid="fulfilled-by">{t('fulfilledBy')}: {o.fulfilled_by.name}</div>}
          {o.receipt && (
            <article data-testid="receipt" lang={o.receipt.language} dir={o.receipt.language === 'ar' ? 'rtl' : 'ltr'}>
              <h3>{t('receipt')}</h3>
              <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
                {o.receipt.language === 'ar' ? <Verbatim text={o.receipt.rendered} /> : o.receipt.rendered}</pre>
            </article>
          )}
        </section>
      ))}
    </main>
  )
}
