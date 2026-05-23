import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { LangProvider } from '@/components/LangProvider'
import EmergencyPage from '@/app/owner/emergency/page'
import OwnerPage from '@/app/owner/page'

describe('EmergencyPage — display-only triage baseline (WI-3)', () => {
  it('renders Arabic guidance immediately, without requiring symptom selection', () => {
    render(<LangProvider><EmergencyPage /></LangProvider>)
    expect(screen.getByText(/إرشادات فورية/)).toBeInTheDocument()
    // Urgent-contact card is visible on first paint — the ≤2-taps invariant
    // means landing on this page IS the guidance, no form required.
    expect(screen.getByText(/جهة الاتصال للطوارئ/)).toBeInTheDocument()
    expect(screen.getByText(/تواصل مع عيادتك البيطرية/)).toBeInTheDocument()
  })

  it('shows the critical banner when a critical symptom is selected and evaluated', async () => {
    const user = userEvent.setup()
    render(<LangProvider><EmergencyPage /></LangProvider>)

    const seizureCheckbox = screen.getByRole('checkbox', { name: /نوبة صرع/ })
    await user.click(seizureCheckbox)
    await user.click(screen.getByRole('button', { name: /تقييم الحالة/ }))

    await waitFor(() => {
      expect(screen.getByRole('status')).toHaveTextContent(/حالة حرجة/)
    })
  })

  it('shows the urgent banner for a species-specific urgent symptom', async () => {
    const user = userEvent.setup()
    render(<LangProvider><EmergencyPage /></LangProvider>)
    await user.click(screen.getByRole('checkbox', { name: /إصابة في العين/ }))
    await user.click(screen.getByRole('button', { name: /تقييم الحالة/ }))
    expect(await screen.findByRole('status')).toHaveTextContent(/حالة عاجلة/)
  })

  it('shows the routine (no red flags) banner when no symptoms are picked', async () => {
    const user = userEvent.setup()
    render(<LangProvider><EmergencyPage /></LangProvider>)
    await user.click(screen.getByRole('button', { name: /تقييم الحالة/ }))
    expect(await screen.findByRole('status')).toHaveTextContent(/لا توجد علامات إنذار/)
  })

  it('includes the no-queue / display-only disclosure', () => {
    render(<LangProvider><EmergencyPage /></LangProvider>)
    expect(screen.getByText(/لا يتم توجيه الحالات تلقائياً/)).toBeInTheDocument()
  })

  it('back-link routes to /owner', () => {
    render(<LangProvider><EmergencyPage /></LangProvider>)
    const back = screen.getByRole('link', { name: /العودة إلى بوابة المالك/ })
    expect(back).toHaveAttribute('href', '/owner')
  })
})

describe('OwnerPage — emergency entry (WI-3 reachability)', () => {
  it('emergency CTA is visible and links directly to /owner/emergency (1 tap)', () => {
    render(<LangProvider><OwnerPage /></LangProvider>)
    const cta = screen.getByRole('link', { name: /حالة طارئة/ })
    expect(cta).toHaveAttribute('href', '/owner/emergency')
  })
})

describe('WI-3 hard boundary — no FR-11 vet queue', () => {
  // Source-level audit: the emergency page must not import anything that
  // would push it toward backend dispatch / vet queue / live routing.
  // This is a deliberate scope-creep tripwire.
  const emergencySrc = readFileSync(
    resolve(__dirname, '../app/owner/emergency/page.tsx'),
    'utf8'
  )
  const triageSrc = readFileSync(
    resolve(__dirname, '../lib/triage.ts'),
    'utf8'
  )

  it('emergency page source does not call fetch / POST / route endpoints', () => {
    // Structural test: NO network dispatch lives in this page. The
    // explanatory comment block in the source MAY mention "queue" /
    // "dispatch" / "routing" to document the FR-11 boundary, so the
    // tripwire checks for actual call sites, not vocabulary.
    expect(emergencySrc).not.toMatch(/\bfetch\s*\(/)
    expect(emergencySrc).not.toMatch(/\.post\s*\(/i)
    expect(emergencySrc).not.toMatch(/axios|XMLHttpRequest|navigator\.sendBeacon/)
  })

  it('triage module is pure: no network or persistence imports', () => {
    expect(triageSrc).not.toMatch(/\bfetch\s*\(/)
    expect(triageSrc).not.toMatch(/localStorage|sessionStorage/)
    expect(triageSrc).not.toMatch(/\bfrom\s+['"]next\//)
  })
})
