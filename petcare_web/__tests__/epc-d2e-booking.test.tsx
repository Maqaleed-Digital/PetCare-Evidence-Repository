/**
 * MVC-EPC-D-001 D2e — CO-05 book and CO-07 my appointments (J-O5). The screens show what the server serves (pets,
 * veterinarians, free slots, bookings) and send only SELECTORS: never an owner, tenant or actor. Cancelling needs an
 * explicit confirmation before the request is sent.
 */
import { fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { LangProvider } from '@/components/LangProvider'
import BookPage from '@/app/owner/book/page'
import AppointmentsPage from '@/app/owner/appointments/page'
import OwnerPage from '@/app/owner/page'

const SLOT = '2031-03-02T06:00:00+00:00'
type Call = [string, RequestInit | undefined]
const calls = () => (fetch as unknown as { mock: { calls: Call[] } }).mock.calls

function serve(routes: Record<string, unknown>) {
  vi.stubGlobal('fetch', vi.fn((url: string, init?: RequestInit) => {
    const path = new URL(url, 'http://x').pathname
    if (init?.method === 'POST') return Promise.resolve(new Response(JSON.stringify({ ok: true }), { status: 201 }))
    return Promise.resolve(new Response(JSON.stringify(routes[path] ?? []), { status: 200 }))
  }))
}

afterEach(() => { vi.unstubAllGlobals(); window.history.replaceState(null, '', '/') })

describe('CO-05 book a consultation (D2e)', () => {
  it('offers the served pets, veterinarians and free slots and posts only selectors', async () => {
    serve({ '/api/pets': [{ pet_id: 'p1', name: 'Luna', species: 'cat' }],
            '/api/booking/veterinarians': [{ user_id: 'u-vet', full_name: 'د. سارة' }],
            '/api/booking/slots': [SLOT] })
    const assign = vi.fn()
    vi.stubGlobal('location', { ...window.location, search: '', assign })
    render(<LangProvider><BookPage /></LangProvider>)
    expect(await screen.findByRole('option', { name: 'Luna · cat' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'د. سارة' })).toBeInTheDocument()
    const slot = await screen.findByRole('radio', { name: /.+/, checked: false })
    fireEvent.click(slot)
    fireEvent.click(screen.getByTestId('book-submit'))
    await vi.waitFor(() => expect(calls().some(([, i]) => i?.method === 'POST')).toBe(true))
    const [url, init] = calls().find(([, i]) => i?.method === 'POST') as Call
    expect(url).toMatch(/\/api\/bookings$/)
    expect(init?.credentials).toBe('include')
    const body = JSON.parse(String(init?.body))
    expect(Object.keys(body).sort()).toEqual(['mode', 'pet_id', 'reason', 'starts_at', 'veterinarian_id'])
    expect(body).toMatchObject({ pet_id: 'p1', veterinarian_id: 'u-vet', starts_at: SLOT, mode: 'IN_CLINIC' })
    await vi.waitFor(() => expect(assign).toHaveBeenCalledWith('/owner/appointments'))
  })

  it('asks for the slots of the chosen veterinarian and day from the server', async () => {
    serve({ '/api/pets': [{ pet_id: 'p1', name: 'Luna', species: 'cat' }],
            '/api/booking/veterinarians': [{ user_id: 'u-vet', full_name: 'د. سارة' }] })
    render(<LangProvider><BookPage /></LangProvider>)
    await vi.waitFor(() => expect(calls().some(([u]) => u.includes('/api/booking/slots?veterinarian_id=u-vet&day='))).toBe(true))
  })
})

describe('CO-07 my appointments (D2e)', () => {
  const BOOKING = { booking_id: 'b1', pet_id: 'p1', veterinarian_id: 'u-vet', mode: 'IN_CLINIC', starts_at: SLOT, status: 'BOOKED' }

  it('lists the served bookings and cancels only after confirmation', async () => {
    serve({ '/api/bookings': [BOOKING], '/api/pets': [{ pet_id: 'p1', name: 'Luna' }],
            '/api/booking/veterinarians': [{ user_id: 'u-vet', full_name: 'د. سارة' }] })
    render(<LangProvider><AppointmentsPage /></LangProvider>)
    expect(await screen.findByText('Luna')).toBeInTheDocument()
    expect(screen.getByTestId('appointment-reschedule')).toHaveAttribute('href', '/owner/book?reschedule=b1&vet=u-vet')
    fireEvent.click(screen.getByTestId('appointment-cancel'))
    expect(calls().some(([, i]) => i?.method === 'POST')).toBe(false)          // one click never cancels
    fireEvent.click(screen.getByTestId('appointment-cancel-confirm'))
    await vi.waitFor(() => expect(calls().some(([u, i]) => i?.method === 'POST' && u.endsWith('/api/bookings/b1/cancel'))).toBe(true))
  })

  it('is loading, not empty, until the server answers', () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {})))
    render(<LangProvider><AppointmentsPage /></LangProvider>)
    expect(document.querySelector('[data-state="loading"]')).not.toBeNull()
    expect(screen.queryByText('لا توجد مواعيد بعد.')).toBeNull()
  })
})

describe('CO-01 owner home links to booking (D2e)', () => {
  it('links to the served booking screens', () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {})))
    render(<LangProvider><OwnerPage /></LangProvider>)
    expect(screen.getByTestId('owner-open-book')).toHaveAttribute('href', '/owner/book')
    expect(screen.getByTestId('owner-open-appointments')).toHaveAttribute('href', '/owner/appointments')
  })
})
