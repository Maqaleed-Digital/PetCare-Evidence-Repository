'use client'

/**
 * HumanEscalationBanner — WI-4 (Register E-01 HITL entry, display-only).
 *
 * Promotes the urgent-contact path on /owner/emergency to a first-class
 * "reach a human" banner. Display + contact entry only — NO routing
 * queue, NO live vet dispatch (FR-11 is P1 commercial and OUT OF SCOPE).
 */

import { useLang } from '@/components/LangProvider'
import { STRINGS } from '@/lib/strings'

export function HumanEscalationBanner() {
  const { t } = useLang()
  const s = STRINGS.humanEscalation

  return (
    <div
      role="region"
      aria-label={t(s.title)}
      data-testid="human-escalation"
      style={{
        padding: 16,
        background: '#fef3f2',
        border: '1.5px solid #fda29b',
        borderRadius: 12,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
        <span aria-hidden="true" style={{ fontSize: 20 }}>🚑</span>
        <div style={{ fontWeight: 800, fontSize: 16, color: '#7a271a' }}>
          {t(s.title)}
        </div>
      </div>
      <p style={{ fontSize: 14, lineHeight: 1.6, color: '#7a271a', margin: 0 }}>
        {t(s.body)}
      </p>
      <p style={{ fontSize: 12, lineHeight: 1.6, color: '#7a271a', marginTop: 8, fontStyle: 'italic' }}>
        {t(s.pilotNote)}
      </p>
    </div>
  )
}
