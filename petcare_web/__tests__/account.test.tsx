import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import AccountPage from '@/app/account/page'
import { Footer } from '@/components/Footer'

describe('/account — settings + PDPL rights surface (MVC-UX-WO-002 mount point)', () => {
  it('renders both PDPL Rights and Consent State sections', () => {
    render(<LangProvider><AccountPage /></LangProvider>)
    expect(screen.getByText(/الإعدادات والحقوق/)).toBeInTheDocument()
    expect(screen.getByTestId('pdpl-rights-entry')).toBeInTheDocument()
    expect(screen.getByTestId('consent-state-view')).toBeInTheDocument()
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
    expect(screen.getByText('owner')).toBeInTheDocument()
  })

  it('Footer carries the PDPL-rights link routing to /account', () => {
    render(<LangProvider><Footer /></LangProvider>)
    const link = screen.getByTestId('footer-pdpl-link')
    expect(link).toHaveAttribute('href', '/account')
  })
})
