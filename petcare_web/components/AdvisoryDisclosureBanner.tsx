'use client'

/**
 * AdvisoryDisclosureBanner — WI-1 (Register P-01 DecisionSupportDisclosure).
 *
 * Tells the owner that Maqaleed Vet by VetiCare *supports* — does not
 * replace — a licensed veterinarian. This is a LIVE pilot fact:
 * the platform is advisory; the vet is the clinical authority.
 *
 * Dismissible-but-persistent: once dismissed the banner stays gone via
 * a per-mount localStorage flag (the caller passes a `storageKey` so
 * different mount points can be dismissed independently).
 */

import { useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'
import { STRINGS } from '@/lib/strings'

interface Props {
  /** localStorage key for the dismissal flag (per mount). */
  storageKey: string
}

export function AdvisoryDisclosureBanner({ storageKey }: Props) {
  const { t } = useLang()
  const s = STRINGS.advisory
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (typeof window === 'undefined') return
    setVisible(!localStorage.getItem(storageKey))
  }, [storageKey])

  if (!visible) return null

  function dismiss() {
    localStorage.setItem(storageKey, 'true')
    setVisible(false)
  }

  return (
    <div
      role="note"
      aria-label={t(s.title)}
      data-testid="advisory-disclosure"
      style={{
        display: 'flex', gap: 12, alignItems: 'flex-start',
        padding: '12px 16px',
        background: '#eef4ff',
        border: '1px solid #b6d1ff',
        borderRadius: 10,
      }}
    >
      <span aria-hidden="true" style={{ fontSize: 18, lineHeight: 1.2 }}>ⓘ</span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4, color: 'var(--accent)' }}>
          {t(s.title)}
        </div>
        <p style={{ fontSize: 13, lineHeight: 1.6, margin: 0, color: 'var(--text)' }}>
          {t(s.body)}
        </p>
      </div>
      <button
        type="button"
        onClick={dismiss}
        className="button button-outline button-sm"
        style={{ flexShrink: 0, minHeight: 36 }}
      >
        {t(s.dismiss)}
      </button>
    </div>
  )
}
