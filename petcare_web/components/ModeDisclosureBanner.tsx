'use client'

/**
 * ModeDisclosureBanner — WI-5 (Register N-02 CapabilityDeferredIndicator).
 *
 * Honestly marks a capability as deliberately deferred ("coming in full
 * launch") rather than silently broken. Used inline on the portal cards
 * whose CTA does not yet take a real action in the pilot.
 *
 * Pure presentation — no state, no I/O. Caller decides where to mount it.
 */

import { useLang } from '@/components/LangProvider'
import { STRINGS } from '@/lib/strings'

interface Props {
  variant?: 'badge' | 'inline'
}

export function ModeDisclosureBanner({ variant = 'badge' }: Props) {
  const { t } = useLang()
  const s = STRINGS.modeDisclosure

  if (variant === 'inline') {
    return (
      <p data-testid="mode-disclosure-inline"
         style={{
           fontSize: 12, lineHeight: 1.6, margin: '6px 0 0',
           color: 'var(--warn)',
         }}>
        <strong>{t(s.deferredBadge)}</strong> — {t(s.deferredHint)}
      </p>
    )
  }

  return (
    <span
      role="note"
      data-testid="mode-disclosure-badge"
      className="badge badge-amber"
      style={{ alignSelf: 'flex-start' }}
      title={t(s.deferredHint)}
    >
      {t(s.deferredBadge)}
    </span>
  )
}
