import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import OwnerRecallsPage from '@/app/owner/recalls/page'

/**
 * AC-FR-19-02 (UI) — an affected owner sees the recall notice in the app (MVC-BUILD-RUNNER-001 U13).
 * Served behaviour: petcare_api/tests/test_fr19_batch_recall.py.
 */

function json(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })

describe('FR-19 owner recall notices', () => {
  it('shows each served recall notice to the owner, Arabic RTL', async () => {
    const fetchMock = vi.fn((_u: string) => json([{ notification_id: 'n-1', recall_id: 'r-1',
      body: 'Recall: vax-19 batch BAD-1 dispensed for your pet', created_at: '2026-09-25T10:00:00Z' }]))
    vi.stubGlobal('fetch', fetchMock)
    const { container } = render(<LangProvider><OwnerRecallsPage /></LangProvider>)
    await waitFor(() => expect(screen.getAllByTestId('recall-notice').length).toBe(1))
    expect(String(fetchMock.mock.calls[0][0]).endsWith('/api/me/recall-notices')).toBe(true)
    expect(container.querySelector('main')?.getAttribute('dir')).toBe('rtl')
    expect(screen.getByText('تنبيهات سحب المنتجات')).toBeTruthy()
    expect(screen.getByTestId('recall-notice').textContent).toContain('BAD-1')
  })

  it('an owner with no affected dispense sees no notice', async () => {
    vi.stubGlobal('fetch', vi.fn(() => json([])))
    render(<LangProvider><OwnerRecallsPage /></LangProvider>)
    await waitFor(() => expect(screen.getByText('لا توجد تنبيهات سحب تخص حيواناتك.')).toBeTruthy())
    expect(screen.queryAllByTestId('recall-notice').length).toBe(0)
  })
})
