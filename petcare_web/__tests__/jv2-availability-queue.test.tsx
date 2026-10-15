import { describe, it, expect, beforeEach, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import VetAvailabilityPage from '@/app/vet/availability/page'
import VetQueuePage from '@/app/vet/queue/page'

/**
 * J-V2 (MVC-EPC-D-001 D3b, R21.4) — UI. Served behaviour: petcare_api/tests/test_epc_d3b_jv2_availability_queue.py.
 * CV-02 publishes exactly the days and hours chosen (unticked days are not sent) and says when the clinic defaults apply;
 * CV-03 shows the server's queue as given and states an empty queue as empty.
 */
function res(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}
const DEFAULTS = { plan_id: null, published_at: null, default_hours: true,
  windows: [0, 1, 2, 3, 4, 5, 6].map(d => ({ weekday: d, opens: '09:00', closes: '17:00' })) }

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })

describe('CV-02 availability', () => {
  it('states the clinic defaults, and publishes only the ticked days with their hours', async () => {
    const fetchMock = vi.fn((_u: string, init?: RequestInit) => init?.method === 'PUT'
      ? res({ plan_id: 'p', published_at: 'x', windows: [] }) : res(DEFAULTS))
    vi.stubGlobal('fetch', fetchMock)
    render(<LangProvider><VetAvailabilityPage /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('availability-defaults')).toBeTruthy())
    for (const d of [4, 5]) fireEvent.click(document.querySelector(`input[name="works-${d}"]`) as HTMLInputElement)  // Friday, Saturday off
    fireEvent.change(document.querySelector('select[name="opens-6"]') as HTMLSelectElement, { target: { value: '10:00' } })
    fireEvent.change(document.querySelector('select[name="closes-6"]') as HTMLSelectElement, { target: { value: '12:30' } })
    fireEvent.submit(screen.getByTestId('availability-form'))
    await waitFor(() => expect(screen.getByTestId('availability-published')).toBeTruthy())
    const [, init] = fetchMock.mock.calls.find(c => c[1]?.method === 'PUT') as [string, RequestInit]
    const sent = JSON.parse(init.body as string).windows as { weekday: number; opens: string; closes: string }[]
    expect(sent.map(w => w.weekday).sort()).toEqual([0, 1, 2, 3, 6])
    expect(sent.find(w => w.weekday === 6)).toEqual({ weekday: 6, opens: '10:00', closes: '12:30' })
    expect((document.querySelector('main') as HTMLElement).textContent).not.toMatch(/[A-Za-z]/)
  })

  it('tells the veterinarian when the server refuses the schedule', async () => {
    vi.stubGlobal('fetch', vi.fn((_u: string, init?: RequestInit) => init?.method === 'PUT' ? res({ detail: {} }, 400) : res(DEFAULTS)))
    render(<LangProvider><VetAvailabilityPage /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('availability-form')).toBeTruthy())
    fireEvent.submit(screen.getByTestId('availability-form'))
    await waitFor(() => expect(screen.getByTestId('availability-invalid')).toBeTruthy())
  })
})

describe('CV-03 queue', () => {
  it('shows the server\'s appointments with the intake marker and the open consultations', async () => {
    vi.stubGlobal('fetch', vi.fn(() => res({
      appointments: [{ booking_id: 'b-1', starts_at: '2031-03-02T07:00:00+00:00', mode: 'IN_CLINIC', pet: { name: 'لونا' },
        owner_name: 'هدى', reason: 'عرج', intake_submitted: true }],
      open_consultations: [{ session_id: 's-1', created_at: '2031-03-01T07:00:00+00:00', mode: 'IN_PERSON', pet: { name: 'لونا' }, owner_name: 'هدى' }],
    })))
    render(<LangProvider><VetQueuePage /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('queue-appointment')).toBeTruthy())
    expect(screen.getByTestId('queue-appointment').getAttribute('data-intake')).toBe('true')
    expect(screen.getByTestId('queue-appointment').textContent).toContain('هدى')
    expect(screen.getByTestId('queue-open-consultation').getAttribute('data-session')).toBe('s-1')
    expect((document.querySelector('main') as HTMLElement).textContent).not.toMatch(/[A-Za-z]/)
  })

  it('states an empty queue as empty', async () => {
    vi.stubGlobal('fetch', vi.fn(() => res({ appointments: [], open_consultations: [] })))
    render(<LangProvider><VetQueuePage /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('queue-no-appointments')).toBeTruthy())
    expect(screen.getByTestId('queue-no-open')).toBeTruthy()
  })
})
