import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import VetPrescriptionsPage from '@/app/vet/prescriptions/page'

/**
 * AC-FR-14-01 (UI) and AC-FR-14-04 (UI) — MVC-BUILD-RUNNER-001 U9. Served-app behaviour:
 * petcare_api/tests/test_fr14_prescriptions.py.
 */

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/vet/prescriptions',
}))

const RX = { prescription_id: 'rx-1', pet_id: 'pet-1', medication_name: 'Amoxicillin', dosage: '50mg', status: 'ISSUED' }

function json(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}

function serve(authority: unknown, queue: unknown[] = [RX]) {
  const fetchMock = vi.fn((url: string, _init?: RequestInit) =>
    String(url).endsWith('/api/practitioners/me/authority') ? json(authority) : json(queue))
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })

describe('FR-14 vet prescriptions page', () => {
  it('a vet in force issues a prescription (no actor or tenant sent) and verifies one — Arabic RTL', async () => {
    const fetchMock = serve({ in_force: true, reason: null })
    const { container } = render(<LangProvider><VetPrescriptionsPage /></LangProvider>)
    await waitFor(() => expect(screen.getAllByTestId('awaiting-item').length).toBe(1))
    expect(container.querySelector('main')?.getAttribute('dir')).toBe('rtl')
    expect(screen.getByText('الوصفات الطبية')).toBeTruthy()
    const form = screen.getByRole('form')
    for (const [name, value] of [['pet_id', 'pet-1'], ['session_id', 's-1'], ['medication_name', 'Amoxicillin'],
      ['dosage', '50mg'], ['instructions', 'bid']]) {
      fireEvent.change(form.querySelector(`[name="${name}"]`)!, { target: { value } })
    }
    fireEvent.submit(form)
    await waitFor(() => expect(fetchMock.mock.calls.some(c => c[1]?.method === 'POST')).toBe(true))
    const post = fetchMock.mock.calls.find(c => c[1]?.method === 'POST')!
    expect(String(post[0]).endsWith('/api/prescriptions')).toBe(true)
    const sent = JSON.parse(String(post[1]!.body))
    for (const k of ['tenant_id', 'actor_id', 'issuing_vet_id', 'role']) expect(k in sent).toBe(false)
    fireEvent.click(screen.getByRole('button', { name: 'تحقق' }))
    await waitFor(() => expect(fetchMock.mock.calls.some(c => String(c[0]).endsWith('/api/prescriptions/rx-1/verify'))).toBe(true))
  })

  it('a vet whose authority expired sees prescribing as unavailable with the attribute and expiry, and cannot submit', async () => {
    const fetchMock = serve({ in_force: false, reason: 'expired at 2026-09-22T10:00:00+00:00' })
    render(<LangProvider><VetPrescriptionsPage /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('prescribing-unavailable')).toBeTruthy())
    expect(screen.getByText('الصفة المطلوبة: طبيب بيطري مرخّص')).toBeTruthy()
    expect(screen.getByTestId('authority-reason').textContent).toMatch(/^انتهت في .*٢٠٢٦/)
    expect((screen.getByTestId('issue-button') as HTMLButtonElement).closest('fieldset')!.disabled).toBe(true)
    fireEvent.submit(screen.getByRole('form'))
    await new Promise(r => setTimeout(r, 20))
    expect(fetchMock.mock.calls.some(c => c[1]?.method === 'POST')).toBe(false)
  })
})
