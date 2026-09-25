import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import OwnerDeliveriesPage from '@/app/owner/deliveries/page'

/**
 * AC-FR-16-01 (UI) — the owner sees the temperature log of a temperature-controlled delivery
 * (MVC-BUILD-RUNNER-001 U12). Served behaviour: petcare_api/tests/test_fr16_delivery.py.
 */

function json(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })

describe('FR-16 owner deliveries page', () => {
  it('shows the temperature log of a cold-chain delivery, including an out-of-range reading (Arabic RTL)', async () => {
    vi.stubGlobal('fetch', vi.fn(() => json([{ delivery_id: 'd-1', product_id: 'vax', cold_chain: true, temp_min_c: 2,
      temp_max_c: 8, status: 'DELIVERED', temperature_log: [
        { recorded_at: '2026-09-25T10:00:00Z', celsius: 4.1, out_of_range: false },
        { recorded_at: '2026-09-25T10:10:00Z', celsius: 11.2, out_of_range: true }] }])))
    const { container } = render(<LangProvider><OwnerDeliveriesPage /></LangProvider>)
    await waitFor(() => expect(screen.getAllByTestId('reading').length).toBe(2))
    expect(container.querySelector('main')?.getAttribute('dir')).toBe('rtl')
    expect(screen.getByText('سجل درجات الحرارة')).toBeTruthy()
    const [ok, hot] = screen.getAllByTestId('reading')
    expect(ok.getAttribute('data-out-of-range')).toBe('false')
    expect(hot.textContent).toContain('خارج النطاق')
    expect(screen.getByText('تم التسليم')).toBeTruthy()
  })
})
