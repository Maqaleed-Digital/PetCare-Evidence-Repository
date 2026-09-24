import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LangProvider } from '@/components/LangProvider'
import SignInPage from '@/app/signin/page'
import RegisterPage from '@/app/register/page'

/**
 * AC-FR-01-01 (UI) — a registered identity signs in and reaches the surface of its
 * role; the account surfaces send no tenant or actor (MVC-BUILD-RUNNER-001 U4).
 * The served-app half is petcare_api/tests/test_fr01_session_identity.py.
 */

const replace = vi.fn()
vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn(), replace }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/',
}))

function json(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}

beforeEach(() => {
  vi.restoreAllMocks()
  replace.mockReset()
  localStorage.clear()
})

async function signInAs(role: string) {
  vi.stubGlobal('fetch', vi.fn((url: string) => String(url).endsWith('/api/auth/sign-in')
    ? json({ user: { user_id: 'u-1', email: 'a@x.test', full_name: 'A', role } })
    : json({ language: 'ar', source: 'default' })))
  render(<LangProvider><SignInPage /></LangProvider>)
  const user = userEvent.setup()
  const inputs = document.querySelectorAll('input')
  await user.type(inputs[0] as HTMLInputElement, 'a@x.test')
  await user.type(inputs[1] as HTMLInputElement, 'pw')
  await user.click(screen.getByRole('button', { name: /دخول|تسجيل/ }))
  await waitFor(() => expect(replace).toHaveBeenCalled())
  return replace.mock.calls[0][0]
}

describe('FR-01 — each role reaches its surface after sign-in', () => {
  it.each([
    ['owner', '/owner'],
    ['veterinarian', '/vet'],
    ['platform_admin', '/admin'],
    ['partner_clinic_admin', '/account'],
  ])('%s -> %s', async (role, surface) => {
    expect(await signInAs(role)).toBe(surface)
  })
})

describe('FR-01 — registration sends the invite and requested role, never a tenant or actor', () => {
  it('posts to /api/auth/register without tenant_id / actor_id', async () => {
    const calls: { url: string; init?: RequestInit }[] = []
    vi.stubGlobal('fetch', vi.fn((url: string, init?: RequestInit) => {
      calls.push({ url: String(url), init })
      return json({ user: { user_id: 'u-2', email: 'n@x.test', full_name: 'N', role: 'owner' } }, 201)
    }))
    render(<LangProvider><RegisterPage /></LangProvider>)
    const user = userEvent.setup()
    await user.type(document.getElementById('reg-name') as HTMLInputElement, 'N')
    await user.type(document.getElementById('reg-email') as HTMLInputElement, 'n@x.test')
    await user.type(document.getElementById('reg-invite') as HTMLInputElement, 'OWNER-PILOT-001')
    const pw = document.querySelector('input[type="password"]') as HTMLInputElement
    await user.type(pw, 'Pw-long-enough-1')
    await user.click(screen.getByRole('button', { name: /تسجيل|إنشاء/ }))
    await waitFor(() => expect(calls.some(c => c.url.endsWith('/api/auth/register'))).toBe(true))
    const body = JSON.parse(String(calls.find(c => c.url.endsWith('/api/auth/register'))!.init!.body))
    expect(body.invite_code).toBe('OWNER-PILOT-001')
    for (const k of ['tenant_id', 'actor_id', 'user_id']) expect(k in body).toBe(false)
  })
})
