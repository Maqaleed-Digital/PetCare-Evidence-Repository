import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { LangProvider } from '@/components/LangProvider'
import { HumanEscalationBanner } from '@/components/HumanEscalationBanner'

describe('HumanEscalationBanner — WI-4 (E-01 HITL entry, display-only)', () => {
  it('renders AR-first with the human-escalation title and contact body', () => {
    render(<LangProvider><HumanEscalationBanner /></LangProvider>)
    expect(screen.getByTestId('human-escalation')).toBeInTheDocument()
    expect(screen.getByText(/هل تحتاج إلى إنسان الآن؟/)).toBeInTheDocument()
    expect(screen.getByText(/تواصل مع عيادتك البيطرية المسجّلة/)).toBeInTheDocument()
  })

  it('includes the explicit "no queue, no automated dispatch" disclosure', () => {
    render(<LangProvider><HumanEscalationBanner /></LangProvider>)
    expect(screen.getByText(/لا توجد قائمة توزيع آلية/)).toBeInTheDocument()
    expect(screen.getByText(/إرشاد ومسار اتصال فقط/)).toBeInTheDocument()
  })

  it('source contains no FR-11 call sites (no fetch / post / dispatch / axios)', () => {
    const src = readFileSync(
      resolve(__dirname, '../components/HumanEscalationBanner.tsx'),
      'utf8'
    )
    expect(src).not.toMatch(/\bfetch\s*\(/)
    expect(src).not.toMatch(/\.post\s*\(/i)
    expect(src).not.toMatch(/axios|XMLHttpRequest|navigator\.sendBeacon/)
  })
})
