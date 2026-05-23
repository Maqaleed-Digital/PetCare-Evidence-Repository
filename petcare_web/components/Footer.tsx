'use client'

/**
 * Footer — pilot governance + PDPL-rights link (MVC-UX-WO-002 WI-2 mount point).
 *
 * Honest pilot disclosure: brand, residency/DPIA status, link to /privacy
 * and to /account#pdpl-rights. No certified-language; pending statuses
 * stay pending.
 */

import { useLang } from '@/components/LangProvider'
import { STRINGS } from '@/lib/strings'

export function Footer() {
  const { t } = useLang()
  const s = STRINGS.footer

  return (
    <footer
      data-testid="site-footer"
      style={{
        marginTop: 48,
        padding: '24px 24px 32px',
        borderTop: '1px solid var(--line)',
        background: '#fff',
        fontSize: 13,
        color: 'var(--muted)',
      }}
    >
      <div style={{
        maxWidth: 1160, margin: '0 auto',
        display: 'flex', flexWrap: 'wrap', gap: 16,
        alignItems: 'center', justifyContent: 'space-between',
      }}>
        <span>{t(s.copyright)}</span>
        <span className="badge badge-amber" style={{ textTransform: 'none', letterSpacing: 0 }}>
          {t(s.pilotBadge)}
        </span>
        <span style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          <a href="/privacy" style={{ color: 'var(--accent)' }}>{t(s.privacy)}</a>
          <a href="/account" style={{ color: 'var(--accent)' }} data-testid="footer-pdpl-link">
            {t(s.pdplRights)}
          </a>
        </span>
      </div>
    </footer>
  )
}
