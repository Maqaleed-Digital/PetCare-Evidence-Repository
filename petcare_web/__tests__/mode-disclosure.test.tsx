import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import { ModeDisclosureBanner } from '@/components/ModeDisclosureBanner'

describe('ModeDisclosureBanner — WI-5 (N-02 CapabilityDeferredIndicator)', () => {
  it('badge variant renders "coming in full launch" in Arabic', () => {
    render(<LangProvider><ModeDisclosureBanner variant="badge" /></LangProvider>)
    expect(screen.getByTestId('mode-disclosure-badge')).toBeInTheDocument()
    expect(screen.getByText(/قادم في الإطلاق الكامل/)).toBeInTheDocument()
  })

  it('badge variant is the default', () => {
    render(<LangProvider><ModeDisclosureBanner /></LangProvider>)
    expect(screen.getByTestId('mode-disclosure-badge')).toBeInTheDocument()
  })

  it('inline variant renders the deferred hint with surrounding context', () => {
    render(<LangProvider><ModeDisclosureBanner variant="inline" /></LangProvider>)
    expect(screen.getByTestId('mode-disclosure-inline')).toBeInTheDocument()
    expect(screen.getByText(/معروضة بشكل صريح خلال التجريب/)).toBeInTheDocument()
  })
})
