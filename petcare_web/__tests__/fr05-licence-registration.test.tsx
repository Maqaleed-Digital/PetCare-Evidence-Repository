import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import RegisterPage from '@/app/register/page'

/**
 * AC-FR-05-01 (UI) — a veterinarian registers WITH licence details (MVC-BUILD-RUNNER-001 U10).
 * Served-app behaviour: petcare_api/tests/test_fr05_licence.py.
 */

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/register',
}))

function json(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })

function fill(id: string, value: string) {
  fireEvent.change(document.getElementById(id)!, { target: { value } })
}

describe('FR-05 veterinarian registration', () => {
  it('asks a veterinarian for licence details (Arabic) and sends them; an owner is not asked', async () => {
    const fetchMock = vi.fn((_u: string, _i?: RequestInit) => json({ detail: { error: 'INVALID_INVITE' } }, 400))
    vi.stubGlobal('fetch', fetchMock)
    render(<LangProvider><RegisterPage /></LangProvider>)
    expect(screen.queryByTestId('licence-fields')).toBeNull()
    fill('reg-role', 'veterinarian')
    expect(screen.getByTestId('licence-fields')).toBeTruthy()
    expect(screen.getByText('رقم الترخيص المهني')).toBeTruthy()
    expect(screen.getByText('لن تتمكن من أي عمل سريري حتى يتم التحقق من ترخيصك.')).toBeTruthy()
    for (const [id, v] of [['reg-name', 'Dr A'], ['reg-email', 'a@vet.test'], ['reg-invite', 'INV-1'],
      ['reg-password', 'Pw-long-enough-1'], ['reg-licence-number', 'MEWA-123'],
      ['reg-licence-authority', 'MEWA'], ['reg-licence-expiry', '2030-01-31']]) fill(id, v)
    fireEvent.submit(document.getElementById('reg-name')!.closest('form')!)
    await waitFor(() => expect(fetchMock).toHaveBeenCalled())
    const sent = JSON.parse(String(fetchMock.mock.calls[0][1]!.body))
    expect(sent.role).toBe('veterinarian')
    expect(sent.licence).toEqual({ licence_number: 'MEWA-123', issuing_authority: 'MEWA', expires_on: '2030-01-31' })
  })

  it('shows the served refusal when licence details are missing or expired', async () => {
    vi.stubGlobal('fetch', vi.fn(() => json({ detail: { error: 'LICENCE_EXPIRED' } }, 400)))
    render(<LangProvider><RegisterPage /></LangProvider>)
    fill('reg-role', 'veterinarian')
    for (const [id, v] of [['reg-name', 'Dr A'], ['reg-email', 'a@vet.test'], ['reg-invite', 'INV-1'],
      ['reg-password', 'Pw-long-enough-1'], ['reg-licence-number', 'M-1'], ['reg-licence-authority', 'MEWA'],
      ['reg-licence-expiry', '2020-01-01']]) fill(id, v)
    fireEvent.submit(document.getElementById('reg-name')!.closest('form')!)
    await waitFor(() => expect(screen.getByRole('alert').textContent).toBe('الترخيص المدخل منتهي الصلاحية.'))
  })
})
