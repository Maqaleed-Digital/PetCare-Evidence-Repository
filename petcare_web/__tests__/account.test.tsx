import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import AccountPage from '@/app/account/page'
import { Footer } from '@/components/Footer'

describe('/account — settings + PDPL rights surface (MVC-UX-WO-002 mount point)', () => {
  it('renders the PDPL Rights section and the server-backed profile, consent ledger and export (MVC-EPC-D-001 D2)', () => {
    render(<LangProvider><AccountPage /></LangProvider>)
    expect(screen.getByText(/الإعدادات والحقوق/)).toBeInTheDocument()
    expect(screen.getByTestId('pdpl-rights-entry')).toBeInTheDocument()
    expect(screen.getByTestId('profile-card')).toBeInTheDocument()
    expect(screen.getByTestId('consent-ledger')).toBeInTheDocument()
    expect(screen.getByTestId('data-export')).toBeInTheDocument()
  })

  it('shows the not-signed-in note when vc_user is absent', () => {
    render(<LangProvider><AccountPage /></LangProvider>)
    expect(screen.getByText(/لم يتم تسجيل الدخول بعد/)).toBeInTheDocument()
  })

  it('shows the signed-in identity when vc_user is present', () => {
    localStorage.setItem('vc_user', JSON.stringify({
      user_id: 'u-1', email: 'owner@test.com',
      name: 'مالك التجريب', role: 'owner',
    }))
    render(<LangProvider><AccountPage /></LangProvider>)
    expect(screen.getByText('مالك التجريب')).toBeInTheDocument()
    // X1 (MVC-EPC-D-001 D2): the role is shown in the reader's language, never as the raw role id.
    expect(screen.getByTestId('account-role')).toHaveTextContent('مالك')
    expect(screen.queryByText('owner')).toBeNull()
  })

  it('Footer carries the PDPL-rights link routing to /account', () => {
    render(<LangProvider><Footer /></LangProvider>)
    const link = screen.getByTestId('footer-pdpl-link')
    expect(link).toHaveAttribute('href', '/account')
  })
})
