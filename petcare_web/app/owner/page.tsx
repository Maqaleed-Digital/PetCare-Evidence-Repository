'use client'

import { useLang } from '@/components/LangProvider'
import { STRINGS } from '@/lib/strings'

export default function OwnerPage() {
  const { t } = useLang()
  const s = STRINGS.owner

  return (
    <main className="stack">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div className="kicker">{t(s.kicker)}</div>
          <div className="title-lg">{t(s.title)}</div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
          <span className="badge badge-green">
            <span className="icon-dot green" />{t(s.auditActive)}
          </span>
          {/* Emergency entry — 1 tap from /owner to /owner/emergency.
              Display-only triage; NOT a vet queue (WI-3 hard boundary). */}
          <a href="/owner/emergency" className="emergency-cta" aria-label={t(s.emergencyCta)}>
            <span aria-hidden="true">🚑</span>
            <span>{t(s.emergencyCta)}</span>
          </a>
        </div>
      </div>

      <p className="muted" style={{ fontSize: 13 }}>{t(s.emergencyHint)}</p>

      <div className="grid cols2">
        <div className="role-card">
          <div className="role-card-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
            </svg>
          </div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>{t(s.petProfileTitle)}</div>
            <p className="subtitle">{t(s.petProfileSub)}</p>
          </div>
          <span className="muted">{t(s.petProfileEmpty)}</span>
        </div>

        <div className="role-card">
          <div className="role-card-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
            </svg>
          </div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>{t(s.timelineTitle)}</div>
            <p className="subtitle">{t(s.timelineSub)}</p>
          </div>
          <span className="muted">{t(s.timelineEmpty)}</span>
        </div>

        <div className="role-card">
          <div className="role-card-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>{t(s.appointmentsTitle)}</div>
            <p className="subtitle">{t(s.appointmentsSub)}</p>
          </div>
          <a className="button button-outline button-sm" href="#">{t(s.appointmentsBook)}</a>
        </div>

        <div className="role-card">
          <div className="role-card-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
            </svg>
          </div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>{t(s.consentTitle)}</div>
            <p className="subtitle">{t(s.consentSub)}</p>
          </div>
          <span className="muted">{t(s.consentEmpty)}</span>
        </div>
      </div>

      <div className="note">
        <span className="muted">{t(s.governanceNote)}</span>
      </div>
    </main>
  )
}
