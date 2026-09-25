import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LangProvider } from '@/components/LangProvider'
import PharmacyPage from '@/app/pharmacy/page'

/**
 * AC-FR-19-01 (UI) — a dispense draws from stock and records the batch (MVC-BUILD-RUNNER-001 U13).
 * Served behaviour: petcare_api/tests/test_fr19_batch_recall.py.
 */

const RX = { prescription_id: 'rx-1', pet_id: 'pet-1', medication_name: 'Amoxicillin', dosage: '50mg', instructions: 'bid',
  status: 'VET_VERIFIED', issued_at: '2026-09-25T09:00:00Z', verified_at: '2026-09-25T09:01:00Z',
  verified_by_vet_id: 'u-vet', issuing_vet_id: 'u-vet' }

function json(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })

describe('FR-19 dispensing records the batch', () => {
  it('sends the stock location, product, batch and quantity with the dispense (Arabic labels)', async () => {
    const fetchMock = vi.fn((url: string, _init?: RequestInit) => {
      const u = String(url)
      if (u.endsWith('/api/inventory/locations')) return json([{ location_id: 'loc-1', name: 'الصيدلية' }])
      if (u.endsWith('/dispense')) return json({ ...RX, status: 'DISPENSED' })
      if (u.includes('/queue/awaiting-dispense')) return json([RX])
      return json([])
    })
    vi.stubGlobal('fetch', fetchMock)
    render(<LangProvider><PharmacyPage /></LangProvider>)
    const user = userEvent.setup()
    await waitFor(() => expect(screen.getAllByTestId('queue-item').length).toBe(1))
    await user.click(screen.getAllByTestId('queue-item')[0])
    await waitFor(() => expect(screen.getByTestId('dispense-origin')).toBeTruthy())
    expect(screen.getByText('رقم التشغيلة')).toBeTruthy()
    fireEvent.change(screen.getByTestId('dispense-origin').querySelector('[name="product_id"]')!, { target: { value: 'amoxi' } })
    fireEvent.change(screen.getByTestId('dispense-origin').querySelector('[name="batch"]')!, { target: { value: 'LOT-7' } })
    await user.click(screen.getByTestId('dispense-button'))
    await waitFor(() => expect(fetchMock.mock.calls.some(c => String(c[0]).endsWith('/dispense'))).toBe(true))
    const post = fetchMock.mock.calls.find(c => String(c[0]).endsWith('/dispense'))!
    expect(JSON.parse(String(post[1]!.body))).toEqual({ location_id: 'loc-1', product_id: 'amoxi', batch: 'LOT-7', quantity: 1 })
  })
})
