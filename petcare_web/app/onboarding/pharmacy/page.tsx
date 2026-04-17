'use client'

import { useLang } from '@/components/LangProvider'
import { STRINGS } from '@/lib/strings'

export default function PharmacyOnboardingPage() {
  const { t } = useLang()
  const s = STRINGS.pharmacyOnboarding

  return (
    <main className="stack">
      <div className="card">
        <div className="kicker">{t(s.kicker)}</div>
        <div className="title-lg">{t(s.title)}</div>
        <p className="subtitle" style={{ maxWidth: 600, marginTop: 8 }}>{t(s.intro)}</p>
      </div>

      <div className="grid cols2">
        <div className="card stack card-sm">
          <div className="badge badge-blue" style={{ alignSelf: 'flex-start' }}>{t(s.step1)}</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>{t(s.step1t)}</div>
            <p className="subtitle">{t(s.step1d)}</p>
          </div>
        </div>
        <div className="card stack card-sm">
          <div className="badge badge-blue" style={{ alignSelf: 'flex-start' }}>{t(s.step2)}</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>{t(s.step2t)}</div>
            <p className="subtitle">{t(s.step2d)}</p>
          </div>
        </div>
        <div className="card stack card-sm">
          <div className="badge badge-blue" style={{ alignSelf: 'flex-start' }}>{t(s.step3)}</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>{t(s.step3t)}</div>
            <p className="subtitle">{t(s.step3d)}</p>
          </div>
        </div>
        <div className="card stack card-sm">
          <div className="badge badge-green" style={{ alignSelf: 'flex-start' }}>{t(s.step4)}</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>{t(s.step4t)}</div>
            <p className="subtitle">{t(s.step4d)}</p>
          </div>
        </div>
      </div>

      <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 24, flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 240 }}>
          <div className="title" style={{ fontSize: 16 }}>{t(s.ctaTitle)}</div>
          <p className="subtitle">{t(s.ctaSub)}</p>
        </div>
        <a className="button" href="mailto:onboarding@myveticare.com">{t(s.ctaBtn)}</a>
      </div>

      <p className="muted" style={{ textAlign: 'center' }}>
        <a href="/onboarding" style={{ color: 'var(--accent)' }}>{t(s.backLink)}</a>
      </p>
    </main>
  )
}
