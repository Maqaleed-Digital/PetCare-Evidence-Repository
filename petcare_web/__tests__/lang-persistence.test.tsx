import { describe, it, expect } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LangProvider, useLang } from '@/components/LangProvider'
import { LanguageToggle } from '@/components/LanguageToggle'

function LangProbe() {
  const { lang } = useLang()
  return <span data-testid="lang-probe">{lang}</span>
}

describe('LangProvider — toggle persistence (WI-2 / April-17 nav event-bus)', () => {
  it('persists the toggled language in localStorage and re-hydrates after a remount', async () => {
    const user = userEvent.setup()
    const { unmount } = render(
      <LangProvider>
        <LanguageToggle />
        <LangProbe />
      </LangProvider>
    )

    expect(screen.getByTestId('lang-probe').textContent).toBe('ar')

    await user.click(screen.getByRole('button'))
    expect(screen.getByTestId('lang-probe').textContent).toBe('en')
    expect(localStorage.getItem('vc_lang')).toBe('en')
    expect(document.documentElement.lang).toBe('en')
    expect(document.documentElement.dir).toBe('ltr')

    unmount()

    render(
      <LangProvider>
        <LangProbe />
      </LangProvider>
    )
    expect(screen.getByTestId('lang-probe').textContent).toBe('en')
    expect(document.documentElement.dir).toBe('ltr')
  })

  it('reverts to Arabic + RTL when toggled back', async () => {
    const user = userEvent.setup()
    localStorage.setItem('vc_lang', 'en')
    render(
      <LangProvider>
        <LanguageToggle />
        <LangProbe />
      </LangProvider>
    )

    await act(async () => { /* allow hydration effect */ })
    expect(screen.getByTestId('lang-probe').textContent).toBe('en')

    await user.click(screen.getByRole('button'))
    expect(screen.getByTestId('lang-probe').textContent).toBe('ar')
    expect(localStorage.getItem('vc_lang')).toBe('ar')
    expect(document.documentElement.dir).toBe('rtl')
  })
})
