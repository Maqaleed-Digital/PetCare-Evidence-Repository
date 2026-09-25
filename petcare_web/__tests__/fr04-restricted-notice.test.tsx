import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import OwnerOrdersPage from '@/app/owner/orders/page'

/**
 * AC-FR-04-01 (UI) — in the purchase flow the purchaser is shown that verification is required for restricted and
 * controlled medicines, and why (MVC-BUILD-RUNNER-001 U17). Served behaviour:
 * petcare_api/tests/test_fr04_restricted_substances.py (every path refused while EV-11 is open).
 */

function json(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })

describe('FR-04 purchase flow notice', () => {
  it('states in Arabic that identity verification is required and why restricted medicines are unavailable', async () => {
    vi.stubGlobal('fetch', vi.fn((url: string) =>
      String(url).endsWith('/api/catalog/prices') ? json([{ product_id: 'collar-20', unit_price_halalas: 2500 }]) : json([])))
    render(<LangProvider><OwnerOrdersPage /></LangProvider>)
    await waitFor(() => expect(screen.getByRole('form')).toBeTruthy())
    const notice = screen.getByTestId('restricted-notice').textContent ?? ''
    expect(notice).toMatch(/التحقق من هوية المشتري/)
    expect(notice).toMatch(/EV-11/)
    expect(notice).toMatch(/معطّل/)
  })
})
