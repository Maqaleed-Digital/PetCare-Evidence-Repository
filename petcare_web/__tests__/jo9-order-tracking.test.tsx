import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import OwnerOrdersPage from '@/app/owner/orders/page'

/**
 * J-O9 internal tracking (MVC-EPC-D-001 D2n, R19.5 item 4) — UI. Served behaviour: petcare_api/tests/test_epc_d2n_jo9_internal_tracking.py.
 * The page shows the order's own lifecycle from `tracking` and states that no courier tracking exists; it never shows a carrier.
 */
function json(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}
const ORDER = { order_id: 'o-9', payment_method: 'COD', status: 'PLACED', paid: false, total_halalas: 1000, receipt: null,
  tracking: { carrier: null, steps: [
    { step: 'PLACED', done: true, at: '2031-03-01T06:00:00+00:00' }, { step: 'ROUTED', done: false, at: null },
    { step: 'DELIVERED', done: false, at: null }, { step: 'RECEIPT_ISSUED', done: false, at: null }] } }

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })

describe('J-O9 owner order tracking', () => {
  it('shows the four lifecycle steps in Arabic with only the placed step done, and no carrier', async () => {
    vi.stubGlobal('fetch', vi.fn((url: string) => json(String(url).endsWith('/api/orders') ? [ORDER] : [])))
    render(<LangProvider><OwnerOrdersPage /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('order-tracking')).toBeTruthy())
    const steps = screen.getAllByTestId('tracking-step')
    expect(steps.map(s => s.getAttribute('data-step'))).toEqual(['PLACED', 'ROUTED', 'DELIVERED', 'RECEIPT_ISSUED'])
    expect(steps.map(s => s.getAttribute('data-done'))).toEqual(['true', 'false', 'false', 'false'])
    expect(steps[0].textContent).toContain('استُلم الطلب')
    expect(steps[1].textContent).toContain('لم يتم بعد')
    expect(screen.getByTestId('tracking-no-carrier').textContent).toMatch(/لا يتوفر تتبّع لدى شركة شحن/)
    expect(screen.getByTestId('order-tracking').textContent).not.toMatch(/[A-Za-z]/)   // no untranslated copy in Arabic
  })

  it('renders English labels when the owner chose English', async () => {
    localStorage.setItem('vc_lang', 'en')
    vi.stubGlobal('fetch', vi.fn((url: string) => json(String(url).endsWith('/api/orders') ? [ORDER] : [])))
    render(<LangProvider><OwnerOrdersPage /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('order-tracking')).toBeTruthy())
    expect(screen.getAllByTestId('tracking-step')[0].textContent).toContain('Order placed')
    expect(screen.getByTestId('tracking-no-carrier').textContent).toMatch(/No courier tracking/)
  })

  it('renders an order without tracking (older API) without failing', async () => {
    const { tracking: _t, ...legacy } = ORDER
    vi.stubGlobal('fetch', vi.fn((url: string) => json(String(url).endsWith('/api/orders') ? [legacy] : [])))
    render(<LangProvider><OwnerOrdersPage /></LangProvider>)
    await waitFor(() => expect(screen.getAllByTestId('order').length).toBe(1))
    expect(screen.queryByTestId('order-tracking')).toBeNull()
  })
})
