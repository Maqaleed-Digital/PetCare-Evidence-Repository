import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LangProvider } from '@/components/LangProvider'
import { AdvisoryDisclosureBanner } from '@/components/AdvisoryDisclosureBanner'

describe('AdvisoryDisclosureBanner — WI-1 (P-01 DecisionSupportDisclosure)', () => {
  it('renders AR-first with the guidance-not-clinical-decision title and body', () => {
    render(
      <LangProvider>
        <AdvisoryDisclosureBanner storageKey="vc_advisory_test_1" />
      </LangProvider>
    )
    expect(screen.getByTestId('advisory-disclosure')).toBeInTheDocument()
    expect(screen.getByText(/إرشاد، وليس قراراً سريرياً/)).toBeInTheDocument()
    expect(screen.getByText(/تدعم الطبيب البيطري المرخّص ولا تحلّ محلّه/)).toBeInTheDocument()
  })

  it('dismissal persists to localStorage under the supplied storageKey', async () => {
    const user = userEvent.setup()
    render(
      <LangProvider>
        <AdvisoryDisclosureBanner storageKey="vc_advisory_test_2" />
      </LangProvider>
    )
    expect(screen.getByTestId('advisory-disclosure')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /فهمت/ }))
    expect(screen.queryByTestId('advisory-disclosure')).not.toBeInTheDocument()
    expect(localStorage.getItem('vc_advisory_test_2')).toBe('true')
  })

  it('does not re-show on subsequent mount when the dismissal flag is set', () => {
    localStorage.setItem('vc_advisory_test_3', 'true')
    render(
      <LangProvider>
        <AdvisoryDisclosureBanner storageKey="vc_advisory_test_3" />
      </LangProvider>
    )
    expect(screen.queryByTestId('advisory-disclosure')).not.toBeInTheDocument()
  })

  it('different mount points dismiss independently (per-key flag)', () => {
    localStorage.setItem('vc_advisory_owner', 'true')
    const { container } = render(
      <LangProvider>
        <div data-testid="wrapper-owner">
          <AdvisoryDisclosureBanner storageKey="vc_advisory_owner" />
        </div>
        <div data-testid="wrapper-emergency">
          <AdvisoryDisclosureBanner storageKey="vc_advisory_emergency" />
        </div>
      </LangProvider>
    )
    // Owner dismissed → 0 banners under wrapper-owner.
    // Emergency not dismissed → 1 banner under wrapper-emergency.
    const banners = container.querySelectorAll('[data-testid="advisory-disclosure"]')
    expect(banners.length).toBe(1)
  })
})
