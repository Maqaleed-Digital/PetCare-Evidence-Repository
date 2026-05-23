import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import { ConsentStateView } from '@/components/ConsentStateView'
import { CONSENT_KEY, writeConsent } from '@/lib/consent'

describe('ConsentStateView — WI-3 (P-06 ConsentOriginMap, read-only)', () => {
  it('renders Arabic intro + section heading', () => {
    render(<LangProvider><ConsentStateView /></LangProvider>)
    expect(screen.getByTestId('consent-state-view')).toBeInTheDocument()
    expect(screen.getByText(/سجل الموافقات المرتبط بحسابك/)).toBeInTheDocument()
  })

  it('shows the no-record fallback when localStorage has no consent', () => {
    render(<LangProvider><ConsentStateView /></LangProvider>)
    expect(screen.getByText(/لا يوجد سجل موافقة محلي لهذا المتصفح/)).toBeInTheDocument()
  })

  it('displays scope + when + origin from a written consent record', () => {
    writeConsent({
      consented_at: '2026-05-24T10:00:00.000Z',
      origin_invite_code: 'OWNER-PILOT-001',
      scope: ['registration', 'privacy_notice'],
    })
    render(<LangProvider><ConsentStateView /></LangProvider>)
    expect(screen.getByText(/تسجيل الحساب التجريبي/)).toBeInTheDocument()
    expect(screen.getByText(/إقرار بسياسة الخصوصية \(PDPL\)/)).toBeInTheDocument()
    expect(screen.getByText(/OWNER-PILOT-001/)).toBeInTheDocument()
    // Date formatting goes through toLocaleString('ar-SA'|'en-GB'); the
    // exact string depends on the Intl backend in the test env. Assert
    // the dt (label) for "when" is present rather than the value.
    expect(screen.getByText(/تاريخ الموافقة/)).toBeInTheDocument()
  })

  it('CONSENT_KEY is the shared contract between writer and reader', () => {
    expect(CONSENT_KEY).toBe('vc_consent')
  })
})
