import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LangProvider } from '@/components/LangProvider'
import RegisterPage from '@/app/register/page'
import { Nav } from '@/components/Nav'

/** MVC-EPC-D-001 D2 — X6: an invite code never reaches browser storage; X1: the nav's role badge is translated. */
vi.mock('next/navigation', () => ({
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  usePathname: () => '/owner',
}))

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })

describe('D2 X6 / X1', () => {
  it('registration keeps no invite code in browser storage', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(new Response(JSON.stringify({
      user: { user_id: 'u-1', email: 'owner@test.com', full_name: 'Test Owner', role: 'owner' } }),
      { status: 201, headers: { 'Content-Type': 'application/json' } }))
    render(<LangProvider><RegisterPage /></LangProvider>)
    const user = userEvent.setup()
    await user.type(screen.getByLabelText(/الاسم الكامل/), 'Test Owner')
    await user.type(screen.getByLabelText(/البريد الإلكتروني/), 'owner@test.com')
    await user.type(screen.getByLabelText(/رمز الدعوة/), 'OWNER-SECRET-CODE-9')
    await user.type(screen.getByLabelText(/كلمة المرور/), 'Pilot2026!')
    await user.click(screen.getByRole('button', { name: /إنشاء الحساب/ }))
    await waitFor(() => expect(localStorage.getItem('vc_consent')).not.toBeNull())
    expect(JSON.stringify({ ...localStorage })).not.toContain('OWNER-SECRET-CODE-9')
    expect(document.cookie).not.toContain('OWNER-SECRET-CODE-9')
  })

  it('the signed-in navigation shows the role in Arabic, never the raw role id', async () => {
    localStorage.setItem('vc_user', JSON.stringify({ user_id: 'u', email: 'o@t', name: 'مالك', role: 'owner' }))
    render(<LangProvider><Nav /></LangProvider>)
    await waitFor(() => expect(screen.getByText('تسجيل الخروج')).toBeInTheDocument())
    expect(screen.getByRole('navigation').textContent).not.toMatch(/\bowner\b/)
    expect(screen.getByRole('navigation').textContent).toContain('مالك')
  })
})
