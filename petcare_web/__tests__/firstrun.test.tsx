import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LangProvider } from '@/components/LangProvider'
import { FirstRunModal } from '@/components/FirstRunModal'
import OwnerPage from '@/app/owner/page'

const FLAG = 'vc_firstrun_done'

function renderWithLang(node: React.ReactElement) {
  return render(<LangProvider>{node}</LangProvider>)
}

describe('FirstRunModal — pilot guided first-run (WI-4)', () => {
  it('shows the AR-first welcome on /owner when the flag is unset', () => {
    renderWithLang(<OwnerPage />)
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByText(/مرحباً بك في VetiCare/)).toBeInTheDocument()
    expect(screen.getByText(/دعنا نبدأ/)).toBeInTheDocument()
  })

  it('does NOT re-show on /owner once the flag is set (non-blocking after completion)', () => {
    localStorage.setItem(FLAG, 'true')
    renderWithLang(<OwnerPage />)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('advances through 3 steps and reveals the primary "add a pet" CTA on the last step', async () => {
    const user = userEvent.setup()
    renderWithLang(<FirstRunModal />)
    // Step 1
    expect(screen.getByText(/ملفك مكتمل/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /التالي/ })).toBeInTheDocument()
    // → Step 2
    await user.click(screen.getByRole('button', { name: /التالي/ }))
    expect(screen.getByText(/أضف أول حيوان أليف/)).toBeInTheDocument()
    // → Step 3
    await user.click(screen.getByRole('button', { name: /التالي/ }))
    expect(screen.getByText(/في الطوارئ، اضغط زر الحالة الطارئة/)).toBeInTheDocument()
    // Final step shows the add-pet primary CTA (not "next")
    expect(screen.queryByRole('button', { name: /التالي/ })).not.toBeInTheDocument()
    const finish = screen.getByRole('link', { name: /إضافة أول حيوان أليف/ })
    expect(finish).toHaveAttribute('href', '/owner#pets')
  })

  it('Skip dismisses the modal and persists the completion flag', async () => {
    const user = userEvent.setup()
    renderWithLang(<FirstRunModal />)
    await user.click(screen.getByRole('button', { name: /تخطّي/ }))
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(localStorage.getItem(FLAG)).toBe('true')
  })

  it('finishing the walkthrough on the last step persists the completion flag', async () => {
    const user = userEvent.setup()
    renderWithLang(<FirstRunModal />)
    await user.click(screen.getByRole('button', { name: /التالي/ }))
    await user.click(screen.getByRole('button', { name: /التالي/ }))
    await user.click(screen.getByRole('link', { name: /إضافة أول حيوان أليف/ }))
    expect(localStorage.getItem(FLAG)).toBe('true')
  })

  it('Escape key closes the modal but does NOT persist (avoids accidental dismissal cost)', async () => {
    const user = userEvent.setup()
    renderWithLang(<FirstRunModal />)
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    await user.keyboard('{Escape}')
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(localStorage.getItem(FLAG)).toBeNull()
  })

  it('clicking the backdrop closes the modal without persisting (accidental click safe)', async () => {
    const user = userEvent.setup()
    renderWithLang(<FirstRunModal />)
    await user.click(screen.getByRole('dialog'))
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(localStorage.getItem(FLAG)).toBeNull()
  })

  it('renders English when language is en', () => {
    localStorage.setItem('vc_lang', 'en')
    renderWithLang(<FirstRunModal />)
    expect(screen.getByText(/Welcome to VetiCare/)).toBeInTheDocument()
    expect(screen.getByText(/Let’s get started/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Skip/ })).toBeInTheDocument()
  })

  it('all primary buttons meet 48px touch target', () => {
    renderWithLang(<FirstRunModal />)
    const skip = screen.getByRole('button', { name: /تخطّي/ }) as HTMLButtonElement
    const next = screen.getByRole('button', { name: /التالي/ }) as HTMLButtonElement
    for (const b of [skip, next]) {
      const min = (b.style.minHeight || '').match(/(\d+)px/)?.[1]
      expect(Number(min ?? 0)).toBeGreaterThanOrEqual(48)
    }
  })
})
