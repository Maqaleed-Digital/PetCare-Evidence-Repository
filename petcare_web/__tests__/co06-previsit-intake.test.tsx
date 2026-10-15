import { describe, it, expect, beforeEach, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import PreVisitIntakePage from '@/app/owner/appointments/[bookingId]/intake/page'

/**
 * CO-06 pre-visit intake (MVC-EPC-D-001 D2p, R21.4) — UI. Served behaviour: petcare_api/tests/test_epc_d2p_co06_previsit_intake.py.
 * No intake yet (404) -> the form; submitting posts the answers and photos as multipart to the booking's intake; a submitted
 * intake is shown read-only with its photo downloads; the server's refusals are told to the owner; at most five photos.
 */
function res(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}
const INTAKE = { intake_id: 'i-1', booking_id: 'b-1', reason: 'يعرج على الساق الخلفية', symptoms_since: '2031-02-26',
  eating_normally: 'NO', current_medications: '', submitted_at: '2031-03-01T06:00:00+00:00',
  photos: [{ photo_id: 'p-1', filename: 'leg.png', byte_size: 70 }] }
const png = (n: string) => new File([new Uint8Array([137, 80, 78, 71])], n, { type: 'image/png' })

function fill() {
  fireEvent.change(document.querySelector('textarea[name="reason"]') as HTMLTextAreaElement, { target: { value: 'يعرج على الساق الخلفية' } })
  fireEvent.click(document.querySelector('input[name="eating_normally"][value="NO"]') as HTMLInputElement)
}

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })

describe('CO-06 pre-visit intake', () => {
  it('shows the form when no intake exists and posts the answers and photos as multipart', async () => {
    const fetchMock = vi.fn((_url: string, init?: RequestInit) => init?.method === 'POST' ? res(INTAKE, 201) : res({}, 404))
    vi.stubGlobal('fetch', fetchMock)
    render(<LangProvider><PreVisitIntakePage params={{ bookingId: 'b-1' }} /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('intake-form')).toBeTruthy())
    fill()
    fireEvent.change(screen.getByTestId('intake-photos'), { target: { files: [png('leg.png')] } })
    fireEvent.submit(screen.getByTestId('intake-form'))
    await waitFor(() => expect(screen.getByTestId('intake-done')).toBeTruthy())
    const [url, init] = fetchMock.mock.calls.find(c => c[1]?.method === 'POST') as [string, RequestInit]
    expect(url).toMatch(/\/api\/bookings\/b-1\/intake$/)
    const body = init.body as FormData
    expect(body.get('reason')).toBe('يعرج على الساق الخلفية')
    expect(body.get('eating_normally')).toBe('NO')
    expect((body.getAll('photos') as File[]).map(f => f.name)).toEqual(['leg.png'])
    expect(screen.getByTestId('intake-eating').getAttribute('data-value')).toBe('NO')
    expect(screen.getAllByTestId('intake-photo').length).toBe(1)
  })

  it('shows a submitted intake read-only, with photo downloads and no form, in Arabic', async () => {
    vi.stubGlobal('fetch', vi.fn(() => res(INTAKE)))
    render(<LangProvider><PreVisitIntakePage params={{ bookingId: 'b-1' }} /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('intake-submitted')).toBeTruthy())
    expect(screen.queryByTestId('intake-form')).toBeNull()
    expect(screen.getByTestId('intake-reason').textContent).toBe('يعرج على الساق الخلفية')
    expect(screen.getByTestId('intake-photo-download').getAttribute('href')).toMatch(/\/api\/bookings\/b-1\/intake\/photos\/p-1$/)
    const main = document.querySelector('main') as HTMLElement
    const copy = main.cloneNode(true) as HTMLElement
    copy.querySelectorAll('[translate="no"]').forEach(n => n.remove())
    expect(copy.textContent).not.toMatch(/[A-Za-z]/)
  })

  it('tells the owner why the server refused (already sent, not upcoming)', async () => {
    for (const [code, text] of [['INTAKE_ALREADY_SUBMITTED', 'سبق إرسال استمارة'], ['BOOKING_NOT_UPCOMING', 'لموعد قادم']]) {
      vi.stubGlobal('fetch', vi.fn((_u: string, init?: RequestInit) =>
        init?.method === 'POST' ? res({ detail: { error: code } }, 409) : res({}, 404)))
      const { unmount } = render(<LangProvider><PreVisitIntakePage params={{ bookingId: 'b-1' }} /></LangProvider>)
      await waitFor(() => expect(screen.getByTestId('intake-form')).toBeTruthy())
      fill()
      fireEvent.submit(screen.getByTestId('intake-form'))
      await waitFor(() => expect(screen.getByTestId('intake-error').textContent).toContain(text))
      unmount()
    }
  })

  it('refuses more than five photos before sending anything', async () => {
    const fetchMock = vi.fn((_u: string, _init?: RequestInit) => res({}, 404))
    vi.stubGlobal('fetch', fetchMock)
    render(<LangProvider><PreVisitIntakePage params={{ bookingId: 'b-1' }} /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('intake-form')).toBeTruthy())
    fill()
    fireEvent.change(screen.getByTestId('intake-photos'), { target: { files: [1, 2, 3, 4, 5, 6].map(i => png(`${i}.png`)) } })
    fireEvent.submit(screen.getByTestId('intake-form'))
    await waitFor(() => expect(screen.getByTestId('intake-error').textContent).toContain('خمس صور'))
    expect(fetchMock.mock.calls.some(c => c[1]?.method === 'POST')).toBe(false)
  })
})
