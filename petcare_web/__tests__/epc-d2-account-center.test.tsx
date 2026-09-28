import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LangProvider } from '@/components/LangProvider'
import { ConsentLedger, DataExportCard, ProfileCard } from '@/components/account/AccountCenter'

/** MVC-EPC-D-001 D2 — J-O2 consent ledger, J-O3 profile + export: the page shows the SERVER's state, never a local one. */
const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
const state = (granted: Record<string, boolean>) => ({
  purposes: ['privacy_notice', 'care_reminders', 'marketing_messages'].map(p => ({
    purpose: p, granted: !!granted[p], since: granted[p] ? '2026-09-28T10:00:00Z' : null, revocable: p !== 'privacy_notice' })),
  history: Object.keys(granted).filter(k => granted[k]).map((p, i) =>
    ({ event_id: `e${i}`, purpose: p, action: 'GRANT', at: '2026-09-28T10:00:00Z' })),
})

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })

describe('D2 account centre', () => {
  it('shows each purpose from the server, offers no withdrawal of the privacy notice, and posts a grant', async () => {
    const fetchMock = vi.spyOn(global, 'fetch')
      .mockResolvedValueOnce(json(state({ privacy_notice: true })))
      .mockResolvedValueOnce(json({ ...state({ privacy_notice: true, care_reminders: true }), changed: true }))
    render(<LangProvider><ConsentLedger /></LangProvider>)
    const pn = await screen.findByTestId('consent-privacy_notice')
    expect(pn).toHaveAttribute('data-granted', 'true')
    expect(within(pn).queryByRole('button')).toBeNull()
    await userEvent.setup().click(screen.getByTestId('consent-care_reminders-grant'))
    await waitFor(() => expect(screen.getByTestId('consent-care_reminders')).toHaveAttribute('data-granted', 'true'))
    const [url, init] = fetchMock.mock.calls[1]
    expect(String(url)).toMatch(/\/api\/me\/consents\/care_reminders$/)
    expect(init).toMatchObject({ method: 'POST', credentials: 'include', body: JSON.stringify({ action: 'GRANT' }) })
    expect(JSON.stringify({ ...localStorage })).not.toMatch(/care_reminders/)       // nothing kept in the browser
  })

  it('shows the error state with a retry when the ledger cannot be read', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(json({}, 500))
    render(<LangProvider><ConsentLedger /></LangProvider>)
    expect(await screen.findByRole('alert')).toBeInTheDocument()
  })

  it('saves only the display name', async () => {
    const fetchMock = vi.spyOn(global, 'fetch')
      .mockResolvedValueOnce(json({ user_id: 'u', email: 'o@t.test', full_name: 'قديم', role: 'owner' }))
      .mockResolvedValueOnce(json({ user_id: 'u', full_name: 'نورة' }))
    render(<LangProvider><ProfileCard /></LangProvider>)
    const input = await screen.findByDisplayValue('قديم')
    const user = userEvent.setup()
    await user.clear(input)
    await user.type(input, 'نورة')
    await user.click(screen.getByRole('button', { name: 'حفظ' }))
    await screen.findByTestId('profile-saved')
    expect(fetchMock.mock.calls[1][1]).toMatchObject({ method: 'PUT', body: JSON.stringify({ full_name: 'نورة' }) })
  })

  it('export: a server enrolment refusal routes the owner to enrolment and downloads nothing', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(json({ detail: { error: 'MFA_ENROLMENT_REQUIRED' } }, 403))
    const create = vi.fn()
    Object.defineProperty(URL, 'createObjectURL', { value: create, configurable: true })
    render(<LangProvider><DataExportCard /></LangProvider>)
    await userEvent.setup().click(screen.getByTestId('data-export-download'))
    expect(await screen.findByTestId('enrolment-required')).toBeInTheDocument()
    expect(create).not.toHaveBeenCalled()
  })
})
