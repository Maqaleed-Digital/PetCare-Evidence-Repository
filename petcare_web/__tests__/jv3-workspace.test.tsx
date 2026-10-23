import { describe, it, expect, beforeEach, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import ConsultationWorkspacePage from '@/app/vet/consultations/[sessionId]/page'
import VetQueuePage from '@/app/vet/queue/page'
import { applyTemplate, EMPTY_SOAP, type SoapTemplate } from '@/lib/soapTemplates'

/**
 * J-V3 (MVC-EPC-D-001 D3c, R21.4) — UI. Served behaviour: petcare_api/tests/test_epc_d3c_jv3_workspace.py.
 * CV-05: a template fills only empty sections; saving sends the four sections and the template; the draft is shown as unsigned
 * and no signing control exists; the outcome completes the visit; a consultation that is not the veterinarian's is not shown.
 */
function res(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}
const TPL: SoapTemplate = { template_id: 'SOAP_GENERAL', name: { ar: 'استشارة عامة', en: 'General consultation' },
  sections: { subjective: { ar: 'سبب الزيارة:', en: 'Reason for visit:' }, objective: { ar: 'نتائج الفحص:', en: 'Examination findings:' },
    assessment: { ar: 'التقييم:', en: 'Assessment:' }, plan: { ar: 'العلاج:', en: 'Treatment:' } } }
const ws = (over: Record<string, unknown> = {}) => ({
  consultation: { session_id: 's-1', mode: 'IN_PERSON', status: 'REQUESTED', created_at: '2031-03-01T07:00:00+00:00', outcome: null },
  pet: { name: 'لونا', species: 'قطة', breed: null }, owner_name: 'هدى', soap: null, soap_versions: 0, templates: [TPL],
  remote: { offered: false }, ...over })
const params = { sessionId: 's-1' }

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })

describe('CV-05 template rule', () => {
  it('fills only the empty sections, in the chosen language', () => {
    const out = applyTemplate({ ...EMPTY_SOAP, subjective: 'يعرج منذ يومين', plan: '   ' }, TPL, 'ar')
    expect(out).toEqual({ subjective: 'يعرج منذ يومين', objective: 'نتائج الفحص:', assessment: 'التقييم:', plan: 'العلاج:' })
    expect(applyTemplate(EMPTY_SOAP, TPL, 'en').objective).toBe('Examination findings:')
  })
})

describe('CV-05 workspace', () => {
  it('applies a template without overwriting, saves an unsigned draft, and offers no signing', async () => {
    const fetchMock = vi.fn((_u: string, init?: RequestInit) => init?.method === 'PUT'
      ? res({ draft_id: 'd-1', status: 'DRAFT' })
      : res(ws()))
    vi.stubGlobal('fetch', fetchMock)
    render(<LangProvider><ConsultationWorkspacePage params={params} /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('soap-form')).toBeTruthy())
    expect(screen.getByTestId('workspace-owner').textContent).toBe('هدى')
    expect(screen.getByTestId('soap-draft-status').getAttribute('data-status')).toBe('NONE')
    fireEvent.change(screen.getByTestId('soap-subjective'), { target: { value: 'يعرج منذ يومين' } })
    fireEvent.change(screen.getByTestId('soap-template'), { target: { value: 'SOAP_GENERAL' } })
    fireEvent.click(screen.getByTestId('soap-apply-template'))
    expect((screen.getByTestId('soap-subjective') as HTMLTextAreaElement).value).toBe('يعرج منذ يومين')
    expect((screen.getByTestId('soap-objective') as HTMLTextAreaElement).value).toBe('نتائج الفحص:')
    fireEvent.submit(screen.getByTestId('soap-form'))
    await waitFor(() => expect(screen.getByTestId('soap-saved')).toBeTruthy())
    const [url, init] = fetchMock.mock.calls.find(c => c[1]?.method === 'PUT') as [string, RequestInit]
    expect(url).toMatch(/\/api\/vet\/consultations\/s-1\/soap$/)
    expect(JSON.parse(init.body as string)).toEqual({ template_id: 'SOAP_GENERAL', subjective: 'يعرج منذ يومين',
      objective: 'نتائج الفحص:', assessment: 'التقييم:', plan: 'العلاج:' })
    expect(document.querySelector('[data-testid*="sign"]')).toBeNull()
    expect((document.querySelector('main') as HTMLElement).textContent).not.toMatch(/[A-Za-z]/)
  })

  it('shows the saved draft from the server and says when the server refuses one', async () => {
    const draft = { draft_id: 'd-2', status: 'DRAFT', template_id: null, subjective: 'حكة', objective: '', assessment: '', plan: '',
      saved_at: '2031-03-01T07:10:00+00:00' }
    vi.stubGlobal('fetch', vi.fn((_u: string, init?: RequestInit) => init?.method === 'PUT' ? res({ detail: {} }, 400)
      : res(ws({ soap: draft, soap_versions: 3 }))))
    render(<LangProvider><ConsultationWorkspacePage params={params} /></LangProvider>)
    await waitFor(() => expect((screen.getByTestId('soap-subjective') as HTMLTextAreaElement).value).toBe('حكة'))
    expect(screen.getByTestId('soap-draft-status').getAttribute('data-versions')).toBe('3')
    fireEvent.submit(screen.getByTestId('soap-form'))
    await waitFor(() => expect(screen.getByTestId('soap-invalid')).toBeTruthy())
  })

  it('records the outcome, after which the visit shows as completed', async () => {
    let done = false
    const fetchMock = vi.fn((u: string, init?: RequestInit) => {
      if (init?.method === 'POST') { done = true; return res({}) }
      return res(done ? ws({ consultation: { session_id: 's-1', mode: 'IN_PERSON', status: 'COMPLETED', created_at: '2031-03-01T07:00:00+00:00',
        outcome: { outcome: 'التواء بسيط' } } }) : ws())
    })
    vi.stubGlobal('fetch', fetchMock)
    render(<LangProvider><ConsultationWorkspacePage params={params} /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('outcome-form')).toBeTruthy())
    fireEvent.change(screen.getByTestId('outcome-text'), { target: { value: 'التواء بسيط' } })
    fireEvent.submit(screen.getByTestId('outcome-form'))
    await waitFor(() => expect(screen.getByTestId('workspace-outcome').textContent).toBe('التواء بسيط'))
    expect(screen.getByTestId('workspace-header').getAttribute('data-status')).toBe('COMPLETED')
    const [url, init] = fetchMock.mock.calls.find(c => c[1]?.method === 'POST') as [string, RequestInit]
    expect(url).toMatch(/\/api\/consultations\/s-1\/outcome$/)
    expect(JSON.parse(init.body as string)).toEqual({ outcome: 'التواء بسيط' })
  })

  it('does not show a consultation that is not the veterinarian\'s', async () => {
    vi.stubGlobal('fetch', vi.fn(() => res({ detail: { error: 'CONSULTATION_NOT_FOUND' } }, 404)))
    render(<LangProvider><ConsultationWorkspacePage params={params} /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('workspace-not-found')).toBeTruthy())
    expect(screen.queryByTestId('soap-form')).toBeNull()
  })
})

describe('CV-03 -> CV-05', () => {
  it('links each open consultation to its workspace', async () => {
    vi.stubGlobal('fetch', vi.fn(() => res({ appointments: [],
      open_consultations: [{ session_id: 's 1', created_at: '2031-03-01T07:00:00+00:00', mode: 'IN_PERSON', pet: { name: 'لونا' }, owner_name: 'هدى' }] })))
    render(<LangProvider><VetQueuePage /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('queue-open-workspace')).toBeTruthy())
    expect(screen.getByTestId('queue-open-workspace').getAttribute('href')).toBe('/vet/consultations/s%201')
  })
})
