import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import OwnerRemindersPage from '@/app/owner/reminders/page'

/**
 * AC-FR-23-01 (UI) and AC-FR-23-02 (ARABIC_RTL) — the owner sees the served reminders, an Arabic reminder
 * right-to-left (MVC-BUILD-RUNNER-001 U15). Served behaviour: petcare_api/tests/test_fr23_reminders.py.
 */

function json(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })

describe('FR-23 owner reminders', () => {
  it('shows the 7-day and 24-hour reminders, Arabic right-to-left', async () => {
    const fetchMock = vi.fn((_u: string) => json([
      { reminder_id: 'r1', kind: 'REMIND_7D', language: 'ar', body: 'تذكير: خلال ٧ أيام — موعد تطعيم «داء الكلب» لحيوانك لونا', sent_at: '2026-09-25T09:00:00Z' },
      { reminder_id: 'r2', kind: 'REMIND_24H', language: 'ar', body: 'تذكير: خلال ٢٤ ساعة — موعد تطعيم «داء الكلب» لحيوانك لونا', sent_at: '2026-09-30T09:00:00Z' },
    ]))
    vi.stubGlobal('fetch', fetchMock)
    const { container } = render(<LangProvider><OwnerRemindersPage /></LangProvider>)
    await waitFor(() => expect(screen.getAllByTestId('reminder').length).toBe(2))
    expect(String(fetchMock.mock.calls[0][0]).endsWith('/api/me/reminders')).toBe(true)
    expect(container.querySelector('main')?.getAttribute('dir')).toBe('rtl')
    for (const el of screen.getAllByTestId('reminder')) expect(el.getAttribute('dir')).toBe('rtl')
    expect(screen.getByText('قبل ٢٤ ساعة')).toBeTruthy()
    expect(screen.getByText('التذكيرات')).toBeTruthy()
  })
})
