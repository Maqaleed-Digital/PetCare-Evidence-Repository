import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import VisitSummaryPage from '@/app/owner/consultations/[sessionId]/summary/page'

/**
 * CO-10 visit summary and care plan (MVC-EPC-D-001 D2q, R21.4) — UI. Served behaviour: petcare_api/tests/test_epc_d2q_co10_visit_summary.py.
 * The page shows the server's summary as written — outcome, this visit's prescriptions, care plan and follow-up — states when
 * there is no care plan or no prescription, and shows no summary for an incomplete visit (409).
 */
function res(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}
const SUMMARY = {
  session_id: 's-1', pet: { pet_id: 'p-1', name: 'لونا' }, veterinarian: { user_id: 'v-1', name: 'د. سلمى' }, mode: 'IN_PERSON',
  visited_at: '2031-03-01T06:00:00+00:00', outcome: { text: 'التواء بسيط؛ راحة ومضاد التهاب.', recorded_at: '2031-03-01T07:00:00+00:00' },
  prescriptions: [{ prescription_id: 'rx-1', medication_name: 'ميلوكسيكام', dosage: '٠٫٥ ملغ', instructions: 'مرة يومياً مع الطعام', status: 'ISSUED' }],
  care_plan: { instructions: 'راحة لمدة سبعة أيام؛ دون قفز.', follow_up_on: '2031-03-15', recorded_at: '2031-03-01T07:05:00+00:00' },
}

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })

describe('CO-10 visit summary', () => {
  it('shows the outcome, this visit\'s prescriptions and the care plan, in Arabic with no untranslated copy', async () => {
    const fetchMock = vi.fn((_u: string) => res(SUMMARY))
    vi.stubGlobal('fetch', fetchMock)
    render(<LangProvider><VisitSummaryPage params={{ sessionId: 's-1' }} /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('visit-summary')).toBeTruthy())
    expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/owner\/consultations\/s-1\/summary$/)
    expect(screen.getByTestId('visit-outcome').textContent).toBe('التواء بسيط؛ راحة ومضاد التهاب.')
    expect(screen.getByTestId('visit-vet').textContent).toBe('د. سلمى')
    expect(screen.getAllByTestId('visit-prescription').map(p => p.textContent)).toEqual(['ميلوكسيكام ٠٫٥ ملغ — مرة يومياً مع الطعام'])
    expect(screen.getByTestId('care-plan-instructions').textContent).toBe('راحة لمدة سبعة أيام؛ دون قفز.')
    expect(screen.getByTestId('care-plan-follow-up').getAttribute('data-date')).toBe('2031-03-15')
    expect((document.querySelector('main') as HTMLElement).textContent).not.toMatch(/[A-Za-z]/)
  })

  it('says when the veterinarian has recorded no care plan and prescribed nothing', async () => {
    vi.stubGlobal('fetch', vi.fn(() => res({ ...SUMMARY, prescriptions: [], care_plan: null })))
    render(<LangProvider><VisitSummaryPage params={{ sessionId: 's-1' }} /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('visit-no-care-plan')).toBeTruthy())
    expect(screen.getByTestId('visit-no-prescriptions')).toBeTruthy()
    expect(screen.queryByTestId('visit-care-plan')).toBeNull()
  })

  it('shows no summary for an incomplete visit (409) and an alert when it is not the owner\'s (404)', async () => {
    vi.stubGlobal('fetch', vi.fn(() => res({ detail: { error: 'VISIT_NOT_COMPLETED' } }, 409)))
    const { unmount } = render(<LangProvider><VisitSummaryPage params={{ sessionId: 's-1' }} /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('visit-not-completed')).toBeTruthy())
    expect(screen.queryByTestId('visit-summary')).toBeNull()
    unmount()
    vi.stubGlobal('fetch', vi.fn(() => res({ detail: 'Consultation not found' }, 404)))
    render(<LangProvider><VisitSummaryPage params={{ sessionId: 's-x' }} /></LangProvider>)
    await waitFor(() => expect(screen.getByRole('alert')).toBeTruthy())
    expect(screen.queryByTestId('visit-summary')).toBeNull()
  })

  it('renders English labels when the owner chose English', async () => {
    localStorage.setItem('vc_lang', 'en')
    vi.stubGlobal('fetch', vi.fn(() => res({ ...SUMMARY, care_plan: { ...SUMMARY.care_plan, follow_up_on: null } })))
    render(<LangProvider><VisitSummaryPage params={{ sessionId: 's-1' }} /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('visit-summary')).toBeTruthy())
    expect(screen.getByRole('heading', { level: 1 }).textContent).toBe('Visit summary and care plan')
    expect(screen.getByTestId('care-plan-follow-up').textContent).toBe('No follow-up set')
  })
})
