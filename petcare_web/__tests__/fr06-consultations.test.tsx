import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import ConsultationsPage from '@/app/account/consultations/page'

/**
 * AC-FR-06-05 (UI) — remote veterinary consultation is not offered before the REG-02 counsel
 * determination (MVC-BUILD-RUNNER-001 U11). Served behaviour: petcare_api/tests/test_fr06_consultation.py.
 */

function json(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}

const C = { session_id: 's-1', pet_id: 'p', mode: 'IN_PERSON', status: 'COMPLETED', created_at: '2026-09-25T09:00:00Z',
  outcome: { outcome: 'التهاب الأذن', recorded_by_actor_id: 'u-v', recorded_at: '2026-09-25T10:00:00Z' } }

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })

describe('FR-06 consultations page', () => {
  it('states remote consultation is not offered and presents no remote or video control (Arabic RTL)', async () => {
    vi.stubGlobal('fetch', vi.fn(() => json({ remote: { offered: false, dependency: 'COUNSEL:REG-02_TELEMEDICINE' },
      consultations: [C] })))
    const { container } = render(<LangProvider><ConsultationsPage /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('remote-not-offered')).toBeTruthy())
    expect(container.querySelector('main')?.getAttribute('dir')).toBe('rtl')
    expect(screen.getByTestId('remote-not-offered').textContent).toMatch(/غير متاحة/)
    expect(container.querySelectorAll('video, button').length).toBe(0)
    expect(screen.getByTestId('consultation-outcome').textContent).toContain('التهاب الأذن')
  })
})
