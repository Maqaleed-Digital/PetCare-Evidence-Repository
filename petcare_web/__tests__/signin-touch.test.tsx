import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import SignInPage from '@/app/signin/page'

vi.mock('next/navigation', () => ({
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
}))

describe('SignInPage — pilot mobile invariants (WI-2)', () => {
  it('inputs and submit button meet the 48px touch-target minimum', () => {
    render(<LangProvider><SignInPage /></LangProvider>)
    const email = screen.getByLabelText(/البريد الإلكتروني/) as HTMLInputElement
    const password = screen.getByLabelText(/كلمة المرور/) as HTMLInputElement
    const submit = screen.getByRole('button', { name: /تسجيل الدخول/ }) as HTMLButtonElement

    for (const el of [email, password, submit]) {
      const min = (el.style.minHeight || '').match(/(\d+)px/)?.[1]
      expect(Number(min ?? 0)).toBeGreaterThanOrEqual(48)
    }
  })

  it('links to /register for invite-code holders (invite-only path)', () => {
    render(<LangProvider><SignInPage /></LangProvider>)
    const link = screen.getByRole('link', { name: /لديك رمز دعوة؟ سجّل الآن/ })
    expect(link).toHaveAttribute('href', '/register')
  })

  it('does not surface a public registration option (still pilot-invite-gated)', () => {
    render(<LangProvider><SignInPage /></LangProvider>)
    expect(screen.getByText(/الوصول بدعوة فقط/)).toBeInTheDocument()
  })
})
