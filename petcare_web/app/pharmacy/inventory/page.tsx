'use client'

/**
 * FR-13 — real-time multi-location inventory (MVC-BUILD-RUNNER-001 U8).
 *
 * Ratified AC-FR-13-01: stock is visible per location for every pharmacy location of the
 * tenant, and a change at one location reaches every authorised session without a manual
 * refresh (REAL_TIME_BOUND = 5 s, p95). The page re-reads the served stock every
 * INVENTORY_REFRESH_MS; a failed refresh keeps the last good view. Balances are derived by
 * the server from the movement ledger (AC-FR-13-02). The form sends no actor, tenant or
 * supply class — the session and the product registration decide; POM/RESTRICTED/CONTROLLED
 * stock is refused by the server for anyone but a veterinarian (AC-FR-13-04, until counsel).
 * Route: /pharmacy/inventory (middleware: vet, admin). Arabic default, RTL.
 */

import { FormEvent, useCallback, useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'
import { INVENTORY_REFRESH_MS, LocationStock, VETERINARIAN_ONLY } from '@/lib/inventory'

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
const call = (path: string, init?: RequestInit) =>
  fetch(`${apiBase}${path}`, { credentials: 'include', cache: 'no-store', ...init })

const L = {
  title: { ar: 'المخزون حسب الموقع', en: 'Stock by location' },
  kicker: { ar: 'بوابة الصيدلية', en: 'Pharmacy portal' },
  none: { ar: 'لا توجد مواقع بعد.', en: 'No locations yet.' },
  empty: { ar: 'لا يوجد مخزون في هذا الموقع.', en: 'No stock at this location.' },
  product: { ar: 'المنتج', en: 'Product' },
  batch: { ar: 'التشغيلة', en: 'Batch' },
  quantity: { ar: 'الكمية', en: 'Quantity' },
  klass: { ar: 'فئة التوريد', en: 'Supply class' },
  vetOnly: { ar: 'للطبيب البيطري فقط', en: 'Veterinarian only' },
  record: { ar: 'تسجيل حركة مخزون', en: 'Record a stock movement' },
  location: { ar: 'الموقع', en: 'Location' },
  to: { ar: 'إلى الموقع', en: 'To location' },
  reason: { ar: 'السبب', en: 'Reason' },
  RECEIPT: { ar: 'استلام', en: 'Receipt' },
  ADJUSTMENT: { ar: 'تعديل', en: 'Adjustment' },
  TRANSFER_OUT: { ar: 'نقل', en: 'Transfer' },
  submit: { ar: 'تسجيل', en: 'Record' },
  error: { ar: 'تعذر إكمال الطلب', en: 'The request could not be completed' },
} as const

export default function InventoryPage() {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  const t = (k: keyof typeof L) => L[k][isAr ? 'ar' : 'en']
  const [locations, setLocations] = useState<LocationStock[]>([])
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    try {
      const r = await call('/api/inventory/stock')
      if (r.ok) setLocations((await r.json()).locations)
    } catch { /* keep the last good view */ }
  }, [])

  useEffect(() => { void load() }, [load])
  useEffect(() => {
    const id = setInterval(() => { void load() }, INVENTORY_REFRESH_MS)
    return () => clearInterval(id)
  }, [load])

  async function record(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const f = new FormData(e.currentTarget)
    const reason = String(f.get('reason') ?? 'RECEIPT')
    const body: Record<string, unknown> = {
      location_id: String(f.get('location_id') ?? ''), product_id: String(f.get('product_id') ?? '').trim(),
      batch: String(f.get('batch') ?? '').trim(), quantity_delta: Number(f.get('quantity_delta') ?? 0), reason,
    }
    if (reason === 'TRANSFER_OUT') body.to_location_id = String(f.get('to_location_id') ?? '')
    const r = await call('/api/inventory/movements', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
    })
    setError(r.ok ? '' : t('error'))
    if (r.ok) await load()
  }

  return (
    <main className="stack" dir={isAr ? 'rtl' : 'ltr'}>
      <div>
        <div className="kicker">{t('kicker')}</div>
        <h1 className="title-lg">{t('title')}</h1>
      </div>
      {locations.length === 0 && <p className="muted">{t('none')}</p>}
      {locations.map(loc => (
        <section key={loc.location_id} className="card" data-testid="inventory-location">
          <h2 className="title-md">{loc.name}</h2>
          {loc.stock.length === 0 ? <p className="muted">{t('empty')}</p> : (
            <table>
              <thead><tr><th>{t('product')}</th><th>{t('batch')}</th><th>{t('quantity')}</th><th>{t('klass')}</th></tr></thead>
              <tbody>
                {loc.stock.map(s => (
                  <tr key={`${s.product_id}/${s.batch}`} data-testid="stock-line">
                    <td>{s.product_id}</td><td>{s.batch}</td><td data-testid="stock-quantity">{s.quantity}</td>
                    <td>{s.supply_class}{VETERINARIAN_ONLY.includes(s.supply_class) ? ` · ${t('vetOnly')}` : ''}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      ))}
      {locations.length > 0 && (
        <form onSubmit={record} className="card stack" aria-label={t('record')}>
          <h2 className="title-md">{t('record')}</h2>
          <label>{t('location')}
            <select name="location_id">{locations.map(l => <option key={l.location_id} value={l.location_id}>{l.name}</option>)}</select>
          </label>
          <label>{t('product')}<input name="product_id" required /></label>
          <label>{t('batch')}<input name="batch" required /></label>
          <label>{t('quantity')}<input name="quantity_delta" type="number" required /></label>
          <label>{t('reason')}
            <select name="reason">
              {(['RECEIPT', 'ADJUSTMENT', 'TRANSFER_OUT'] as const).map(r => <option key={r} value={r}>{t(r)}</option>)}
            </select>
          </label>
          <label>{t('to')}
            <select name="to_location_id">{locations.map(l => <option key={l.location_id} value={l.location_id}>{l.name}</option>)}</select>
          </label>
          <button type="submit" className="btn">{t('submit')}</button>
          {error && <p role="alert">{error}</p>}
        </form>
      )}
    </main>
  )
}
