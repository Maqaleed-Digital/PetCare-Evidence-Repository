import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import OwnerOrdersPage from '@/app/owner/orders/page'

/**
 * AC-FR-15-04 (UI) — the owner can see which pharmacy fulfils the order (MVC-BUILD-RUNNER-001 U18).
 * Served behaviour: petcare_api/tests/test_fr15_routing.py.
 */

function json(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })

describe('FR-15 routed order', () => {
  it('shows the routed pharmacy to the owner, in Arabic', async () => {
    vi.stubGlobal('fetch', vi.fn((url: string) => String(url).endsWith('/api/orders')
      ? json([{ order_id: 'o-1', payment_method: 'COD', status: 'PLACED', paid: false, total_halalas: 1000, receipt: null,
          fulfilled_by: { location_id: 'ph-2', name: 'صيدلية الجنوب' } }])
      : json([])))
    render(<LangProvider><OwnerOrdersPage /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('fulfilled-by')).toBeTruthy())
    expect(screen.getByTestId('fulfilled-by').textContent).toBe('تُنفَّذ من صيدلية: صيدلية الجنوب')
  })

  it('shows no pharmacy for an order not yet routed', async () => {
    vi.stubGlobal('fetch', vi.fn((url: string) => String(url).endsWith('/api/orders')
      ? json([{ order_id: 'o-2', payment_method: 'COD', status: 'PLACED', paid: false, total_halalas: 1000, receipt: null,
          fulfilled_by: null }])
      : json([])))
    render(<LangProvider><OwnerOrdersPage /></LangProvider>)
    await waitFor(() => expect(screen.getAllByTestId('order').length).toBe(1))
    expect(screen.queryByTestId('fulfilled-by')).toBeNull()
  })
})
