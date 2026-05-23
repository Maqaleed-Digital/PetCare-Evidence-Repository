import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import { PDPLRightsEntry } from '@/components/PDPLRightsEntry'

const DPO = 'dpo@myveticare.com'

describe('PDPLRightsEntry — WI-2 (P-03 Art 12 access + P-04 Art 18 erasure)', () => {
  it('renders both rights with Arabic-first copy', () => {
    render(<LangProvider><PDPLRightsEntry /></LangProvider>)
    expect(screen.getByText(/حق الوصول إلى بياناتك \(المادة 12\)/)).toBeInTheDocument()
    expect(screen.getByText(/حق المحو \(المادة 18\)/)).toBeInTheDocument()
  })

  it('access CTA is a DPO-routed mailto with PDPL Art 12 subject', () => {
    render(<LangProvider><PDPLRightsEntry /></LangProvider>)
    const cta = screen.getByTestId('pdpl-access-cta')
    const href = cta.getAttribute('href') ?? ''
    expect(href).toMatch(/^mailto:dpo@myveticare\.com/)
    expect(decodeURIComponent(href)).toContain('[PDPL Art 12] Data access request')
  })

  it('erasure CTA is a DPO-routed mailto with PDPL Art 18 subject', () => {
    render(<LangProvider><PDPLRightsEntry /></LangProvider>)
    const cta = screen.getByTestId('pdpl-erasure-cta')
    const href = cta.getAttribute('href') ?? ''
    expect(href).toMatch(/^mailto:dpo@myveticare\.com/)
    expect(decodeURIComponent(href)).toContain('[PDPL Art 18] Data erasure request')
  })

  it('honestly states the statutory window — no fake "instant" claim', () => {
    render(<LangProvider><PDPLRightsEntry /></LangProvider>)
    // The phrase appears in both the access-card body and the bottom
    // statutory note — both are honest restatements. Use a more
    // specific regex pinned to the bottom statutory note.
    expect(screen.getByText(/الرد يتم خلال المهلة النظامية/)).toBeInTheDocument()
    expect(screen.getByText(/لا توجد معالجة آلية فورية في مرحلة التجريب/)).toBeInTheDocument()
  })

  it('lists the DPO email as the contact channel', () => {
    render(<LangProvider><PDPLRightsEntry /></LangProvider>)
    const link = screen.getByText(DPO).closest('a')
    expect(link).not.toBeNull()
    expect(link!.getAttribute('href')).toBe(`mailto:${DPO}`)
  })
})
