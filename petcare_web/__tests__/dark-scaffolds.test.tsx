import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import { FEATURE_AI } from '@/lib/featureFlags'
import { ConfidenceBand } from '@/components/ConfidenceBand'
import { ExplainabilityPanel } from '@/components/ExplainabilityPanel'
import { AuditTrailLink } from '@/components/AuditTrailLink'

describe('WI-6/7/8 dark scaffolds — render nothing while FEATURE_AI is OFF', () => {
  it('FEATURE_AI defaults to false in the pilot (honesty rule baseline)', () => {
    // If this ever flips true without ratification, the dark scaffolds
    // light up at build time. That is the tripwire.
    expect(FEATURE_AI).toBe(false)
  })

  it('WI-6 ConfidenceBand renders null when FEATURE_AI is OFF', () => {
    const { container } = render(
      <LangProvider><ConfidenceBand confidence={0.92} /></LangProvider>
    )
    expect(container.firstChild).toBeNull()
    expect(screen.queryByTestId('confidence-band')).not.toBeInTheDocument()
  })

  it('WI-7 ExplainabilityPanel renders null when FEATURE_AI is OFF', () => {
    const { container } = render(
      <LangProvider>
        <ExplainabilityPanel summary="x" inputs={['a']} sources={['s']} />
      </LangProvider>
    )
    expect(container.firstChild).toBeNull()
    expect(screen.queryByTestId('explainability-panel')).not.toBeInTheDocument()
  })

  it('WI-8 AuditTrailLink renders null when FEATURE_AI is OFF (even with a non-null handle)', () => {
    const { container } = render(
      <LangProvider>
        <AuditTrailLink eventHandle={{ audit_event_id: 'evt-1', occurred_at: '2026-05-24T00:00:00Z' }} />
      </LangProvider>
    )
    expect(container.firstChild).toBeNull()
    expect(screen.queryByTestId('audit-trail-link')).not.toBeInTheDocument()
  })

  it('AuditTrailLink also renders null when the handle is null (pilot in-memory case)', () => {
    const { container } = render(
      <LangProvider><AuditTrailLink eventHandle={null} /></LangProvider>
    )
    expect(container.firstChild).toBeNull()
  })
})
