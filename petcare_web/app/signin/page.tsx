'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import { useLang } from '@/components/LangProvider'
import { STRINGS } from '@/lib/strings'

const ROLE_REDIRECT: Record<string, string> = {
  platform_admin: '/admin',
  // Canonical id (petcare_api/roles.py). Reaches self-service only, per the
  // middleware's DOMAIN_CAPABILITY_PENDING_ROLE_BINDING; was the dead key `clinic_admin`.
  partner_clinic_admin: '/account',
  veterinarian: '/vet',
  owner: '/owner',
}

function setRoleCookie(role: string) {
  const maxAge = 60 * 60 * 12
  document.cookie = `petcare_role=${encodeURIComponent(role)}; path=/; max-age=${maxAge}; samesite=lax`
}

export default function SignInPage() {
  const router = useRouter()
  const { t, setLanguage } = useLang()
  const s = STRINGS.signin
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)

    const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')

    try {
      const res = await fetch(`${apiBase}/api/auth/sign-in`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      })

      if (res.status === 401) { setError(t(s.errInvalid)); return }
      if (res.status === 403) { setError(t(s.errInactive)); return }
      if (!res.ok) { setError(`${t(s.errFailed)} (${res.status})`); return }

      const data = await res.json()
      const role: string = data?.user?.role ?? ''
      setRoleCookie(role)
      if (typeof window !== 'undefined') {
        localStorage.setItem('vc_user', JSON.stringify({
          user_id: data.user.user_id,
          email:   data.user.email,
          name:    data.user.full_name || data.user.email,
          role:    data.user.role,
        }))
        window.dispatchEvent(new Event('vc_user_changed'))
        // FR-09 (U3): restore the language this identity chose in any earlier
        // session. A failure keeps the current language; it never blocks sign-in.
        try {
          const pref = await fetch(`${apiBase}/api/me/preferences/language`, { credentials: 'include' })
          if (pref.ok) {
            const p = await pref.json()
            if (p?.source === 'stored' && (p.language === 'ar' || p.language === 'en')) setLanguage(p.language)
          }
        } catch { /* keep current language */ }
      }
      router.replace(ROLE_REDIRECT[role] ?? '/')
    } catch {
      setError(t(s.errNetwork))
    } finally {
      setLoading(false)
    }
  }

  return (
    <main style={{ maxWidth: 480, margin: '80px auto', padding: '0 24px' }}>
      <div className="card stack" style={{ padding: 40 }}>
        <div>
          <div className="kicker">{t(s.kicker)}</div>
          <div className="title-lg">{t(s.title)}</div>
          <p className="subtitle" style={{ marginTop: 6 }}>{t(s.sub)}</p>
        </div>

        <form onSubmit={handleSubmit} className="stack" style={{ gap: 16 }}>
          <div>
            <label htmlFor="email" style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: 'var(--text)' }}>
              {t(s.emailLabel)}
            </label>
            <input
              id="email" type="email" autoComplete="email" required
              value={email} onChange={e => setEmail(e.target.value)}
              style={{ width: '100%', padding: '12px 14px', minHeight: 48, border: '1px solid var(--line)', borderRadius: 8, fontSize: 14, outline: 'none', background: '#fff' }}
            />
          </div>

          <div>
            <label htmlFor="password" style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: 'var(--text)' }}>
              {t(s.passwordLabel)}
            </label>
            <input
              id="password" type="password" autoComplete="current-password" required
              value={password} onChange={e => setPassword(e.target.value)}
              style={{ width: '100%', padding: '12px 14px', minHeight: 48, border: '1px solid var(--line)', borderRadius: 8, fontSize: 14, outline: 'none', background: '#fff' }}
            />
          </div>

          {error && (
            <div style={{ padding: '10px 14px', background: 'var(--warn-bg)', border: '1px solid #f0a86d', borderRadius: 8, fontSize: 13, color: 'var(--warn)' }}>
              {error}
            </div>
          )}

          <button type="submit" disabled={loading} className="button"
            style={{ width: '100%', justifyContent: 'center', minHeight: 48, opacity: loading ? 0.65 : 1 }}>
            {loading ? t(s.submitting) : t(s.submit)}
          </button>
        </form>

        <p className="muted" style={{ textAlign: 'center', fontSize: 12 }}>{t(s.noSelfReg)}</p>
        <p style={{ textAlign: 'center', fontSize: 13 }}>
          <a href="/register" style={{ color: 'var(--accent)', fontWeight: 600 }}>{t(s.registerCta)}</a>
        </p>
        <p className="muted" style={{ textAlign: 'center' }}>
          <a href="/" style={{ color: 'var(--accent)' }}>{t(s.backHome)}</a>
        </p>
      </div>
    </main>
  )
}
