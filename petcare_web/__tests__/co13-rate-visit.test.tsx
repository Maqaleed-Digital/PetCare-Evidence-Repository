import { describe, it, expect, beforeEach, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import RateVisitPage from '@/app/owner/consultations/[sessionId]/rate/page'

/**
 * CO-13 rate visit (MVC-EPC-D-001 D2r, R21.4) — UI. Served behaviour: petcare_api/tests/test_epc_d2r_co13_rate_visit.py.
 * Not yet rated (404) -> the form; a rating posts the chosen score and comment once and then shows what the server recorded; an
 * existing rating is shown read-only; the server's refusals are told to the owner.
 */
function res(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}
const RATED = { session_id: 's-1', score: 4, comment: 'طبيب لطيف جداً', rated_at: '2031-03-01T08:00:00+00:00' }

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })

describe('CO-13 rate visit', () => {
  it('posts the chosen score and comment once and shows the recorded rating', async () => {
    const fetchMock = vi.fn((_u: string, init?: RequestInit) => init?.method === 'POST' ? res(RATED, 201) : res({}, 404))
    vi.stubGlobal('fetch', fetchMock)
    render(<LangProvider><RateVisitPage params={{ sessionId: 's-1' }} /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('rate-form')).toBeTruthy())
    fireEvent.click(document.querySelector('input[name="score"][value="4"]') as HTMLInputElement)
    fireEvent.change(document.querySelector('textarea[name="comment"]') as HTMLTextAreaElement, { target: { value: 'طبيب لطيف جداً' } })
    fireEvent.submit(screen.getByTestId('rate-form'))
    await waitFor(() => expect(screen.getByTestId('rate-thanks')).toBeTruthy())
    const [url, init] = fetchMock.mock.calls.find(c => c[1]?.method === 'POST') as [string, RequestInit]
    expect(url).toMatch(/\/api\/owner\/consultations\/s-1\/rating$/)
    expect(JSON.parse(init.body as string)).toEqual({ score: 4, comment: 'طبيب لطيف جداً' })
    expect(screen.getByTestId('rate-score').getAttribute('data-score')).toBe('4')
    expect(screen.queryByTestId('rate-form')).toBeNull()
    expect((document.querySelector('main') as HTMLElement).textContent).not.toMatch(/[A-Za-z]/)
  })

  it('shows an existing rating read-only, with no form', async () => {
    vi.stubGlobal('fetch', vi.fn(() => res(RATED)))
    render(<LangProvider><RateVisitPage params={{ sessionId: 's-1' }} /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('rate-done')).toBeTruthy())
    expect(screen.queryByTestId('rate-form')).toBeNull()
    expect(screen.getByTestId('rate-comment').textContent).toBe('طبيب لطيف جداً')
  })

  it('tells the owner why the server refused (not completed, already rated)', async () => {
    for (const [code, text] of [['VISIT_NOT_COMPLETED', 'بعد اكتمالها'], ['VISIT_ALREADY_RATED', 'سبق تقييم']]) {
      vi.stubGlobal('fetch', vi.fn((_u: string, init?: RequestInit) =>
        init?.method === 'POST' ? res({ detail: { error: code } }, 409) : res({}, 404)))
      const { unmount } = render(<LangProvider><RateVisitPage params={{ sessionId: 's-1' }} /></LangProvider>)
      await waitFor(() => expect(screen.getByTestId('rate-form')).toBeTruthy())
      fireEvent.click(document.querySelector('input[name="score"][value="5"]') as HTMLInputElement)
      fireEvent.submit(screen.getByTestId('rate-form'))
      await waitFor(() => expect(screen.getByTestId('rate-error').textContent).toContain(text))
      unmount()
    }
  })

  it('renders English labels when the owner chose English', async () => {
    localStorage.setItem('vc_lang', 'en')
    vi.stubGlobal('fetch', vi.fn(() => res(RATED)))
    render(<LangProvider><RateVisitPage params={{ sessionId: 's-1' }} /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('rate-done')).toBeTruthy())
    expect(screen.getByTestId('rate-score').textContent).toBe('4 out of 5')
  })
})
