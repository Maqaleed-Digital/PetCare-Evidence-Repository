'use client'

/**
 * ConsentStateView — WI-3 (Register P-06 ConsentOriginMap).
 *
 * Read-only view of the user's pilot consent record: what they consented
 * to, when, and the origin (pilot invite vs other future origins).
 * Source: lib/consent.ts (browser-local in the pilot — no Cloud SQL).
 */

import { useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'
import { STRINGS } from '@/lib/strings'
import { readConsent, type ConsentRecord } from '@/lib/consent'

function formatTimestamp(iso: string, lang: 'ar' | 'en'): string {
  try {
    const d = new Date(iso)
    return d.toLocaleString(lang === 'ar' ? 'ar-SA' : 'en-GB', {
      year: 'numeric', month: 'long', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
    })
  } catch {
    return iso
  }
}

export function ConsentStateView() {
  const { t, lang } = useLang()
  const s = STRINGS.consentState
  const [record, setRecord] = useState<ConsentRecord | null>(null)
  const [hydrated, setHydrated] = useState(false)

  useEffect(() => {
    setRecord(readConsent())
    setHydrated(true)
  }, [])

  if (!hydrated) return null

  return (
    <section
      aria-label={STRINGS.account.sectionConsent.en}
      data-testid="consent-state-view"
      className="card stack"
    >
      <div>
        <div className="kicker">{t(STRINGS.account.sectionConsent)}</div>
        <p className="subtitle" style={{ marginTop: 8 }}>{t(s.intro)}</p>
      </div>

      {record === null ? (
        <p className="muted" style={{ fontSize: 13 }}>{t(s.noRecord)}</p>
      ) : (
        <dl style={{
          display: 'grid', gridTemplateColumns: 'max-content 1fr',
          rowGap: 10, columnGap: 16, fontSize: 14, margin: 0,
        }}>
          <dt style={{ fontWeight: 700, color: 'var(--muted)' }}>{t(s.consentedTo)}</dt>
          <dd style={{ margin: 0 }}>
            <ul style={{ margin: 0, paddingInlineStart: 18 }}>
              {record.scope.map(item => (
                <li key={item}>
                  {item === 'registration'    && t(s.scopeRegistration)}
                  {item === 'privacy_notice'  && t(s.scopePrivacyNotice)}
                  {item !== 'registration' && item !== 'privacy_notice' && item}
                </li>
              ))}
            </ul>
          </dd>

          <dt style={{ fontWeight: 700, color: 'var(--muted)' }}>{t(s.consentedAt)}</dt>
          <dd style={{ margin: 0 }}>{formatTimestamp(record.consented_at, lang)}</dd>

          <dt style={{ fontWeight: 700, color: 'var(--muted)' }}>{t(s.origin)}</dt>
          <dd style={{ margin: 0 }}>
            {t(s.originPilotInvite).replace('{{code}}', record.origin_invite_code)}
          </dd>
        </dl>
      )}
    </section>
  )
}
