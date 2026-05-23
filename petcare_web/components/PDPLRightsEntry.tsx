'use client'

/**
 * PDPLRightsEntry — WI-2 (Register P-03 PDPL Art 12 + P-04 PDPL Art 18).
 *
 * Surfaces the user's two pilot-actionable PDPL rights: access (Art 12)
 * and erasure (Art 18). The mechanism in the pilot is a DPO-routed
 * channel — a mailto: with pre-filled subject. The copy honestly states
 * that response happens within the statutory window; we do not claim an
 * instant automated mechanism (because we don't have one).
 */

import { useLang } from '@/components/LangProvider'
import { STRINGS } from '@/lib/strings'

const DPO_EMAIL = 'dpo@myveticare.com'

function mailto(subject: string): string {
  return `mailto:${DPO_EMAIL}?subject=${encodeURIComponent(subject)}`
}

export function PDPLRightsEntry() {
  const { t } = useLang()
  const s = STRINGS.pdplRights

  return (
    <section
      aria-label={STRINGS.account.sectionRights.en}
      data-testid="pdpl-rights-entry"
      className="card stack"
    >
      <div>
        <div className="kicker">{t(STRINGS.account.sectionRights)}</div>
        <p className="subtitle" style={{ marginTop: 8 }}>{t(s.intro)}</p>
      </div>

      <div className="grid cols2">
        <div className="card card-sm stack">
          <div className="title" style={{ fontSize: 15 }}>{t(s.accessTitle)}</div>
          <p className="subtitle">{t(s.accessBody)}</p>
          <a
            href={mailto('[PDPL Art 12] Data access request')}
            className="button button-outline button-sm"
            style={{ alignSelf: 'flex-start', minHeight: 44 }}
            data-testid="pdpl-access-cta"
          >
            {t(s.accessCta)}
          </a>
        </div>

        <div className="card card-sm stack">
          <div className="title" style={{ fontSize: 15 }}>{t(s.erasureTitle)}</div>
          <p className="subtitle">{t(s.erasureBody)}</p>
          <a
            href={mailto('[PDPL Art 18] Data erasure request')}
            className="button button-outline button-sm"
            style={{ alignSelf: 'flex-start', minHeight: 44 }}
            data-testid="pdpl-erasure-cta"
          >
            {t(s.erasureCta)}
          </a>
        </div>
      </div>

      <p className="muted" style={{ fontSize: 12, lineHeight: 1.6 }}>
        {t(s.statutoryNote)}
      </p>
      <p className="muted" style={{ fontSize: 12 }}>
        <strong>{t(s.dpoContact)}: </strong>
        <a href={`mailto:${DPO_EMAIL}`} style={{ color: 'var(--accent)' }}>{DPO_EMAIL}</a>
      </p>
    </section>
  )
}
