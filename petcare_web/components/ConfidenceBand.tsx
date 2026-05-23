'use client'

/**
 * ConfidenceBand — WI-6 DARK SCAFFOLD (Register C-02).
 *
 * Trust surface for AI/agent confidence. Built, wired, gated behind
 * FEATURE_AI. Renders nothing while the flag is OFF so we never display
 * a confidence score for an engine that is not running (honesty rule
 * from MVC-UX-WO-002).
 */

import { FEATURE_AI } from '@/lib/featureFlags'
import { useLang } from '@/components/LangProvider'
import { STRINGS } from '@/lib/strings'

interface Props {
  /** Confidence in [0, 1]. Producer-supplied — no client-side guessing. */
  confidence: number
}

const TIERS: Array<{ min: number; label: { ar: string; en: string }; color: string }> = [
  { min: 0.85, label: { ar: 'مرتفع',   en: 'High' },   color: '#027a48' },
  { min: 0.65, label: { ar: 'متوسط',   en: 'Medium' }, color: '#b54708' },
  { min: 0,    label: { ar: 'منخفض',   en: 'Low' },    color: '#b42318' },
]

export function ConfidenceBand({ confidence }: Props) {
  // Honesty rule: never render confidence for an engine that's not running.
  if (!FEATURE_AI) return null

  const { t } = useLang()
  const s = STRINGS.confidenceBand
  const clamped = Math.max(0, Math.min(1, confidence))
  const tier = TIERS.find(tt => clamped >= tt.min)!

  return (
    <span
      role="meter"
      aria-label={t(s.label)}
      aria-valuenow={Math.round(clamped * 100)}
      aria-valuemin={0}
      aria-valuemax={100}
      data-testid="confidence-band"
      style={{
        display: 'inline-flex', alignItems: 'center', gap: 6,
        padding: '4px 10px', borderRadius: 999,
        background: tier.color + '22', color: tier.color,
        fontSize: 12, fontWeight: 700,
      }}
    >
      <span aria-hidden="true" style={{
        width: 8, height: 8, borderRadius: 999, background: tier.color,
      }} />
      {t(s.label)}: {t(tier.label)} ({Math.round(clamped * 100)}%)
    </span>
  )
}
