import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import PharmacyPage from '@/app/pharmacy/page'
import { QUEUE_REFRESH_MS } from '@/lib/pharmacyQueue'

/**
 * AC-FR-27-01 (UI) — the dispensing dashboard updates WITHOUT a manual refresh
 * (MVC-BUILD-RUNNER-001 U6). REAL_TIME_BOUND = 5 s; the UI contributes at most one
 * refresh interval, which must be well inside the bound.
 */

const RX = {
  prescription_id: 'rx-new', pet_id: 'pet-1', medication_name: 'Amoxicillin', dosage: '50mg',
  instructions: 'bid', status: 'VET_VERIFIED', issued_at: '2026-09-24T09:00:00Z',
  verified_at: '2026-09-24T09:01:00Z', verified_by_vet_id: 'u-vet', issuing_vet_id: 'u-vet',
}

function json(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}

beforeEach(() => { vi.useFakeTimers(); localStorage.clear() })
afterEach(() => { vi.useRealTimers(); vi.restoreAllMocks() })

describe('FR-27 dashboard — refreshes itself inside the ratified bound', () => {
  it('the refresh interval leaves room inside REAL_TIME_BOUND = 5 s', () => {
    expect(QUEUE_REFRESH_MS).toBeGreaterThan(0)
    expect(QUEUE_REFRESH_MS).toBeLessThanOrEqual(2500)
  })

  it('a newly verified prescription appears with no user action', async () => {
    let served: unknown[] = []
    vi.stubGlobal('fetch', vi.fn(() => json(served)))
    render(<LangProvider><PharmacyPage /></LangProvider>)
    await act(async () => { await vi.advanceTimersByTimeAsync(10) })
    expect(screen.queryAllByTestId('queue-item').length).toBe(0)
    served = [RX]
    await act(async () => { await vi.advanceTimersByTimeAsync(QUEUE_REFRESH_MS) })
    expect(screen.getAllByTestId('queue-item').length).toBe(1)
  })

  it('a failed refresh keeps the last good queue on screen', async () => {
    let fail = false
    vi.stubGlobal('fetch', vi.fn(() => fail ? Promise.reject(new Error('network')) : json([RX])))
    render(<LangProvider><PharmacyPage /></LangProvider>)
    await act(async () => { await vi.advanceTimersByTimeAsync(10) })
    expect(screen.getAllByTestId('queue-item').length).toBe(1)
    fail = true
    await act(async () => { await vi.advanceTimersByTimeAsync(QUEUE_REFRESH_MS) })
    expect(screen.getAllByTestId('queue-item').length).toBe(1)
  })
})
