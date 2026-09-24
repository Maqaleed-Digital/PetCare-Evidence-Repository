import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LangProvider } from '@/components/LangProvider'
import MessagesPage from '@/app/account/messages/page'

/**
 * AC-FR-07-01 (UI + ARABIC_RTL) — consultation messages and file sharing
 * (MVC-BUILD-RUNNER-001 U7). Served-app behaviour: petcare_api/tests/test_consultation_messaging.py.
 */

vi.mock('next/navigation', () => ({
  useSearchParams: () => new URLSearchParams('consultation=c-1'),
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  usePathname: () => '/account/messages',
}))

const MSGS = [{ message_id: 'm-1', sender_role: 'veterinarian', body: 'Here is the lab report',
  created_at: '2026-09-24T10:00:00Z', attachments: [{ attachment_id: 'a-1', filename: 'cbc.png', byte_size: 72 }] }]

function json(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })

describe('FR-07 consultation messages page', () => {
  it('renders Arabic RTL and shows the thread with a download link from the served API', async () => {
    const fetchMock = vi.fn((_u: string, _i?: RequestInit) => json(MSGS))
    vi.stubGlobal('fetch', fetchMock)
    const { container } = render(<LangProvider><MessagesPage /></LangProvider>)
    await screen.findByText('Here is the lab report', {}, { timeout: 5000 })
    expect(container.querySelector('main')?.getAttribute('dir')).toBe('rtl')
    expect(screen.getByRole('heading', { level: 1 }).textContent).toBe('رسائل الاستشارة')
    const link = screen.getByRole('link', { name: /cbc.png/ })
    expect(link.getAttribute('href')).toMatch(/\/api\/consultations\/c-1\/messages\/m-1\/attachments\/a-1$/)
    expect(fetchMock.mock.calls[0][0]).toMatch(/\/api\/consultations\/c-1\/messages$/)
  })

  it('sends a message and uploads an attached file, with no actor/tenant in the body', async () => {
    const calls: { url: string; init?: RequestInit }[] = []
    vi.stubGlobal('fetch', vi.fn((u: string, i?: RequestInit) => {
      calls.push({ url: String(u), init: i })
      if (i?.method === 'POST' && String(u).endsWith('/messages')) return json({ message_id: 'm-2' })
      return json(i?.method === 'POST' ? { attachment_id: 'a-2' } : [])
    }))
    render(<LangProvider><MessagesPage /></LangProvider>)
    const form = await screen.findByRole('form', { name: 'إرسال' }, { timeout: 5000 })
    const user = userEvent.setup()
    await user.type(within(form).getByLabelText('الرسالة'), 'Luna is coughing')
    await user.upload(within(form).getByLabelText(/إرفاق/), new File([new Uint8Array([137, 80, 78, 71])], 'x.png', { type: 'image/png' }))
    await user.click(within(form).getByRole('button', { name: 'إرسال' }))
    await waitFor(() => expect(calls.some(c => c.url.endsWith('/messages/m-2/attachments'))).toBe(true), { timeout: 5000 })
    const post = calls.find(c => c.init?.method === 'POST' && c.url.endsWith('/messages'))!
    expect(JSON.parse(String(post.init!.body))).toEqual({ body: 'Luna is coughing' })
  })
})
