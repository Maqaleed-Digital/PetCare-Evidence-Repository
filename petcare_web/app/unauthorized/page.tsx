'use client'

import { useSearchParams } from 'next/navigation'
import { Suspense } from 'react'
import { useLang } from '@/components/LangProvider'
import { STRINGS } from '@/lib/strings'

function UnauthorizedContent() {
  const searchParams = useSearchParams()
  const from = searchParams.get('from') ?? ''
  const required = searchParams.get('required')?.split(',') ?? []
  const { t } = useLang()
  const s = STRINGS.unauthorized

  const roleLabels: Record<string, { ar: string; en: string }> = s.roles

  return (
    <main style={{ maxWidth: 520, margin: '80px auto', padding: '0 24px' }}>
      <div className="card stack" style={{ textAlign: 'center', padding: 40 }}>
        <div>
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ margin: '0 auto' }}>
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
        </div>
        <div>
          <div className="title-lg">{t(s.title)}</div>
          <p className="subtitle">
            {from
              ? t(s.subFrom).replace('{from}', from)
              : t(s.subGeneric)}
          </p>
        </div>

        {required.length > 0 && (
          <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
            <span className="muted" style={{ alignSelf: 'center' }}>{t(s.requiredRole)}</span>
            {required.map(r => (
              <span key={r} className="badge badge-blue">
                {roleLabels[r as keyof typeof roleLabels]
                  ? t(roleLabels[r as keyof typeof roleLabels])
                  : r}
              </span>
            ))}
          </div>
        )}

        <div className="divider" />
        <p className="muted">{t(s.body)}</p>

        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <a className="button" href="/signin">{t(s.ctaSignIn)}</a>
          <a className="button button-outline" href="/">{t(s.ctaHome)}</a>
        </div>
      </div>
    </main>
  )
}

export default function UnauthorizedPage() {
  return (
    <Suspense>
      <UnauthorizedContent />
    </Suspense>
  )
}
