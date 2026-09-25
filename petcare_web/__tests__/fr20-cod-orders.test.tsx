import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import OwnerOrdersPage from '@/app/owner/orders/page'

/**
 * AC-FR-20-01 (UI) and AC-FR-20-02 (UI, ARABIC_RTL) — MVC-BUILD-RUNNER-001 U14.
 * Served behaviour: petcare_api/tests/test_fr20_cod_receipt.py.
 */

function json(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}

const RECEIPT = 'إيصال رقمي — الطلب o-1\nطريقة الدفع: الدفع عند الاستلام\nالإجمالي المحصّل: 25.00 ر.س'

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })

describe('FR-20 owner orders', () => {
  it('checks out with cash on delivery, sending product and quantity only (no price, owner or tenant)', async () => {
    const fetchMock = vi.fn((url: string, _i?: RequestInit) =>
      String(url).endsWith('/api/catalog/prices') ? json([{ product_id: 'collar-20', unit_price_halalas: 2500 }]) : json([]))
    vi.stubGlobal('fetch', fetchMock)
    render(<LangProvider><OwnerOrdersPage /></LangProvider>)
    await waitFor(() => expect(screen.getByRole('form')).toBeTruthy())
    expect(screen.getByLabelText(/الدفع عند الاستلام/)).toBeTruthy()
    fireEvent.change(document.querySelector('[name="qty-collar-20"]')!, { target: { value: '2' } })
    fireEvent.submit(screen.getByRole('form'))
    await waitFor(() => expect(fetchMock.mock.calls.some(c => c[1]?.method === 'POST')).toBe(true))
    const post = fetchMock.mock.calls.find(c => c[1]?.method === 'POST')!
    expect(String(post[0]).endsWith('/api/orders')).toBe(true)
    expect(JSON.parse(String(post[1]!.body))).toEqual({ lines: [{ product_id: 'collar-20', quantity: 2 }], payment_method: 'COD' })
  })

  it('shows the persisted digital receipt of a delivered order in Arabic, right-to-left', async () => {
    vi.stubGlobal('fetch', vi.fn((url: string) => String(url).endsWith('/api/orders')
      ? json([{ order_id: 'o-1', payment_method: 'COD', status: 'DELIVERED', paid: true, total_halalas: 2500,
          receipt: { receipt_id: 'r-1', language: 'ar', rendered: RECEIPT, issued_at: '2026-09-25T10:00:00Z' } }])
      : json([])))
    const { container } = render(<LangProvider><OwnerOrdersPage /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('receipt')).toBeTruthy())
    expect(container.querySelector('main')?.getAttribute('dir')).toBe('rtl')
    expect(screen.getByTestId('receipt').getAttribute('dir')).toBe('rtl')
    expect(screen.getByTestId('receipt').textContent).toContain('إيصال رقمي')
    expect(screen.getByText(/تم التسليم والدفع/)).toBeTruthy()
  })
})
