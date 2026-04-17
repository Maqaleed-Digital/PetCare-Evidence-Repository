'use client'
export const dynamic = 'force-dynamic'

import { useLang } from '@/components/LangProvider'
import { STRINGS } from '@/lib/strings'

export default function HomePage() {
  const { t } = useLang()
  const s = STRINGS.home

  return (
    <main className="stack">
      {/* Hero */}
      <div className="hero">
        <div className="hero-eyebrow">{t(s.eyebrow)}</div>
        <h1 className="hero-title">
          {t(s.h1).split('\n').map((line, i) => (
            <span key={i}>{line}{i === 0 && <br />}</span>
          ))}
        </h1>
        <p className="hero-sub">{t(s.sub)}</p>
        <div className="hero-actions">
          <a className="button button-white" href="/signin">{t(s.ctaSignIn)}</a>
          <a className="button button-ghost" href="/onboarding">{t(s.ctaOnboard)}</a>
        </div>
      </div>

      {/* Role portals */}
      <div>
        <p className="kicker">{t(s.portalsLabel)}</p>
        <div className="grid cols2" style={{ marginTop: 12 }}>
          <div className="role-card">
            <div className="role-card-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
              </svg>
            </div>
            <div>
              <div className="title" style={{ fontSize: 16 }}>{t(s.owner)}</div>
              <p className="subtitle">{t(s.ownerSub)}</p>
            </div>
            <a className="button button-outline button-sm" href="/owner">{t(s.ownerCta)}</a>
          </div>
          <div className="role-card">
            <div className="role-card-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
              </svg>
            </div>
            <div>
              <div className="title" style={{ fontSize: 16 }}>{t(s.vet)}</div>
              <p className="subtitle">{t(s.vetSub)}</p>
            </div>
            <a className="button button-outline button-sm" href="/vet">{t(s.vetCta)}</a>
          </div>
          <div className="role-card">
            <div className="role-card-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <line x1="12" y1="8" x2="12" y2="16"/>
                <line x1="8" y1="12" x2="16" y2="12"/>
              </svg>
            </div>
            <div>
              <div className="title" style={{ fontSize: 16 }}>{t(s.pharmacy)}</div>
              <p className="subtitle">{t(s.pharmacySub)}</p>
            </div>
            <a className="button button-outline button-sm" href="/pharmacy">{t(s.pharmacyCta)}</a>
          </div>
          <div className="role-card">
            <div className="role-card-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
            </div>
            <div>
              <div className="title" style={{ fontSize: 16 }}>{t(s.admin)}</div>
              <p className="subtitle">{t(s.adminSub)}</p>
            </div>
            <a className="button button-outline button-sm" href="/admin">{t(s.adminCta)}</a>
          </div>
        </div>
      </div>

      {/* Governance strip */}
      <div className="card card-sm" style={{ display: 'flex', gap: 24, flexWrap: 'wrap', alignItems: 'center' }}>
        <span className="badge badge-green"><span className="icon-dot green" />{t(s.statusOk)}</span>
        <span className="muted">{t(s.govActive)}</span>
        <span className="muted">·</span>
        <span className="muted">{t(s.auditLive)}</span>
        <span className="muted">·</span>
        <span className="muted">{t(s.pilotPhase)}</span>
      </div>
    </main>
  )
}
