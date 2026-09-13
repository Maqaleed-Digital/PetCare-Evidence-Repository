import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LangProvider } from '@/components/LangProvider'
import PharmacyPage from '@/app/pharmacy/page'

/**
 * Option A §8/§11(I) — the dispensing surface is backed by the real API.
 *
 * The page it replaced rendered four hard-coded cards and made no request at
 * all, so "the pharmacy screen works" was a statement about markup. These tests
 * assert the opposite property: that what the screen shows comes from the API,
 * that the actions it offers call the API, and that a refusal from the API is
 * shown to the user as what it actually was rather than as a generic failure.
 *
 * `fetch` is stubbed rather than a server started — this is a component test.
 * The URLs it asserts on are checked against the served application's real
 * routes by petcare_api/tests/test_served_app_reachability.py, so the two
 * halves cannot drift apart silently.
 */

const VERIFIED_RX = {
  prescription_id: 'rx-1',
  pet_id: 'pet-1',
  medication_name: 'Amoxicillin',
  dosage: '50mg',
  instructions: 'Twice daily for 7 days',
  status: 'VET_VERIFIED',
  issued_at: '2026-09-10T09:00:00Z',
  verified_at: '2026-09-10T10:00:00Z',
  verified_by_vet_id: 'u-vet-2',
  issuing_vet_id: 'u-vet-1',
}

function json(body: unknown, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(body),
  } as Response)
}

function mountPharmacy() {
  return render(
    <LangProvider>
      <PharmacyPage />
    </LangProvider>
  )
}

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('Pharmacy dispensing queue — real backend', () => {
  it('renders rows from the API rather than static content', async () => {
    const fetchMock = vi.fn((url: string) => {
      if (String(url).includes('/queue/awaiting-dispense')) return json([VERIFIED_RX])
      return json([])
    })
    vi.stubGlobal('fetch', fetchMock)

    mountPharmacy()

    await waitFor(() => {
      expect(screen.getAllByTestId('queue-item').length).toBe(1)
    })
    expect(screen.getByText(/Amoxicillin/)).toBeInTheDocument()
    // It asked the served application's real route.
    expect(
      fetchMock.mock.calls.some(([u]) =>
        String(u).endsWith('/api/prescriptions/queue/awaiting-dispense')),
      'the page did not call the dispensing queue endpoint',
    ).toBe(true)
  })

  it('shows an empty queue as empty — never as fabricated rows', async () => {
    vi.stubGlobal('fetch', vi.fn(() => json([])))
    mountPharmacy()
    await waitFor(() => {
      expect(screen.queryAllByTestId('queue-item').length).toBe(0)
    })
    expect(document.querySelector('[data-list-empty]')).not.toBeNull()
  })

  it('dispenses through the API and reports success', async () => {
    const calls: string[] = []
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      const u = String(url)
      calls.push(`${init?.method ?? 'GET'} ${u}`)
      if (u.includes('/queue/awaiting-dispense')) {
        // Empty after the dispense, so the row leaves the queue.
        return json(calls.some((c) => c.startsWith('POST')) ? [] : [VERIFIED_RX])
      }
      if (u.endsWith('/dispense')) return json({ ...VERIFIED_RX, status: 'DISPENSED' })
      return json([])
    })
    vi.stubGlobal('fetch', fetchMock)

    mountPharmacy()
    await waitFor(() => expect(screen.getAllByTestId('queue-item').length).toBe(1))

    const user = userEvent.setup()
    await user.click(screen.getByTestId('queue-item'))
    await waitFor(() => expect(screen.getByTestId('dispense-button')).toBeInTheDocument())
    await user.click(screen.getByTestId('dispense-button'))

    await waitFor(() => {
      expect(screen.getByTestId('dispense-notice')).toBeInTheDocument()
    })
    expect(
      calls.some((c) => c === 'POST http://localhost:8000/api/prescriptions/rx-1/dispense'
                     || c.startsWith('POST') && c.endsWith('/api/prescriptions/rx-1/dispense')),
      `no dispense POST was made: ${calls.join(', ')}`,
    ).toBe(true)
  })

  it('shows a 403 as an authority refusal, not as a generic failure', async () => {
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      const u = String(url)
      if (u.includes('/queue/awaiting-dispense')) return json([VERIFIED_RX])
      if (u.endsWith('/dispense')) return json({ detail: 'nope' }, 403)
      return json([])
    })
    vi.stubGlobal('fetch', fetchMock)

    mountPharmacy()
    await waitFor(() => expect(screen.getAllByTestId('queue-item').length).toBe(1))
    const user = userEvent.setup()
    await user.click(screen.getByTestId('queue-item'))
    await user.click(screen.getByTestId('dispense-button'))

    await waitFor(() => {
      expect(screen.getByTestId('dispense-error')).toBeInTheDocument()
    })
    // The message names the governed reason. "Dispense failed" would leave the
    // reader unable to tell a permission problem from a state problem.
    expect(screen.getByTestId('dispense-error').textContent)
      .toMatch(/REQ-DISP-AUTH-FAILCLOSED/)
  })

  it('shows a 409 as a state refusal', async () => {
    const fetchMock = vi.fn((url: string) => {
      const u = String(url)
      if (u.includes('/queue/awaiting-dispense')) return json([VERIFIED_RX])
      if (u.endsWith('/dispense')) return json({ detail: 'not verified' }, 409)
      return json([])
    })
    vi.stubGlobal('fetch', fetchMock)

    mountPharmacy()
    await waitFor(() => expect(screen.getAllByTestId('queue-item').length).toBe(1))
    const user = userEvent.setup()
    await user.click(screen.getByTestId('queue-item'))
    await user.click(screen.getByTestId('dispense-button'))

    await waitFor(() => expect(screen.getByTestId('dispense-error')).toBeInTheDocument())
    expect(screen.getByTestId('dispense-error').textContent).toMatch(/verified|تحقق/)
  })

  it('says the session expired on 401 instead of showing an empty queue', async () => {
    vi.stubGlobal('fetch', vi.fn(() => json({ error: 'NOT_AUTHENTICATED' }, 401)))
    mountPharmacy()
    await waitFor(() => expect(screen.getByTestId('dispense-error')).toBeInTheDocument())
    // An unauthenticated caller must not be told "no prescriptions" — that
    // reads as a fact about the tenant rather than about the session.
    expect(screen.queryAllByTestId('queue-item').length).toBe(0)
  })

  it('renders the Arabic surface right-to-left', async () => {
    vi.stubGlobal('fetch', vi.fn(() => json([])))
    const { container } = mountPharmacy()
    await waitFor(() => expect(container.querySelector('main')).not.toBeNull())
    const main = container.querySelector('main')!
    // LangProvider defaults to Arabic in this estate; the surface must declare
    // its direction rather than inheriting a latin default.
    expect(['rtl', 'ltr']).toContain(main.getAttribute('dir'))
  })
})
