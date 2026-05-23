'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import { useLang } from '@/components/LangProvider'
import { STRINGS } from '@/lib/strings'
import { writeConsent } from '@/lib/consent'

const ROLE_REDIRECT: Record<string, string> = {
  platform_admin: '/admin',
  clinic_admin: '/admin',
  veterinarian: '/vet',
  owner: '/owner',
}

function setRoleCookie(role: string) {
  const maxAge = 60 * 60 * 12
  document.cookie = `petcare_role=${encodeURIComponent(role)}; path=/; max-age=${maxAge}; samesite=lax`
}

const TOUCH_TARGET = 48

export default function RegisterPage() {
  const router = useRouter()
  const { t, lang } = useLang()
  const s = STRINGS.register

  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [inviteCode, setInviteCode] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState<'owner' | 'veterinarian'>('owner')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)

    const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')

    try {
      const res = await fetch(`${apiBase}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          email, password, invite_code: inviteCode, role, name,
          phone: phone || null,
        }),
      })

      if (!res.ok) {
        let code = ''
        try { code = (await res.json())?.detail?.error ?? '' } catch { /* ignore */ }
        if (code === 'INVALID_INVITE')      { setError(t(s.errInvalidInvite)); return }
        if (code === 'INVITE_EXPIRED')      { setError(t(s.errInviteExpired)); return }
        if (code === 'ROLE_MISMATCH')       { setError(t(s.errRoleMismatch));  return }
        if (code === 'EMAIL_EXISTS')        { setError(t(s.errEmailExists));   return }
        setError(`${t(s.errFailed)} (${res.status})`)
        return
      }

      const data = await res.json()
      const userRole: string = data?.user?.role ?? ''
      setRoleCookie(userRole)
      if (typeof window !== 'undefined') {
        localStorage.setItem('vc_user', JSON.stringify({
          user_id: data.user.user_id,
          email:   data.user.email,
          name:    data.user.full_name || data.user.email,
          role:    data.user.role,
        }))
        // MVC-UX-WO-002 WI-3: write a browser-local consent record so
        // /account ConsentStateView can show what was consented to,
        // when, and the origin (the pilot invite code).
        writeConsent({
          consented_at: new Date().toISOString(),
          origin_invite_code: inviteCode,
          scope: ['registration', 'privacy_notice'],
        })
        window.dispatchEvent(new Event('vc_user_changed'))
      }
      router.replace(ROLE_REDIRECT[userRole] ?? '/')
    } catch {
      setError(t(s.errNetwork))
    } finally {
      setLoading(false)
    }
  }

  const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '12px 14px',
    minHeight: TOUCH_TARGET,
    border: '1px solid var(--line)',
    borderRadius: 8,
    fontSize: 14,
    outline: 'none',
    background: '#fff',
    textAlign: lang === 'ar' ? 'right' : 'left',
  }
  const labelStyle: React.CSSProperties = {
    display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6,
    color: 'var(--text)',
  }

  return (
    <main style={{ maxWidth: 520, margin: '48px auto', padding: '0 16px' }}>
      <div className="card stack" style={{ padding: 32 }}>
        <div>
          <span className="badge badge-blue" style={{ marginBottom: 12, display: 'inline-block' }}>
            {t(s.inviteOnlyBadge)}
          </span>
          <div className="kicker">{t(s.kicker)}</div>
          <div className="title-lg">{t(s.title)}</div>
          <p className="subtitle" style={{ marginTop: 6 }}>{t(s.sub)}</p>
        </div>

        <form onSubmit={handleSubmit} className="stack" style={{ gap: 16 }}>
          <div>
            <label htmlFor="reg-name" style={labelStyle}>{t(s.nameLabel)}</label>
            <input id="reg-name" type="text" required autoComplete="name"
              value={name} onChange={e => setName(e.target.value)}
              style={inputStyle} />
          </div>

          <div>
            <label htmlFor="reg-email" style={labelStyle}>{t(s.emailLabel)}</label>
            <input id="reg-email" type="email" required autoComplete="email"
              value={email} onChange={e => setEmail(e.target.value)}
              style={inputStyle} />
          </div>

          <div>
            <label htmlFor="reg-phone" style={labelStyle}>{t(s.phoneLabel)}</label>
            <input id="reg-phone" type="tel" autoComplete="tel"
              value={phone} onChange={e => setPhone(e.target.value)}
              style={inputStyle} />
          </div>

          <div>
            <label htmlFor="reg-invite" style={labelStyle}>{t(s.inviteLabel)}</label>
            <input id="reg-invite" type="text" required autoComplete="off"
              value={inviteCode} onChange={e => setInviteCode(e.target.value)}
              style={inputStyle} />
          </div>

          <div>
            <label htmlFor="reg-role" style={labelStyle}>{t(s.roleLabel)}</label>
            <select id="reg-role"
              value={role}
              onChange={e => setRole(e.target.value as 'owner' | 'veterinarian')}
              style={inputStyle}>
              <option value="owner">{t(s.roleOwner)}</option>
              <option value="veterinarian">{t(s.roleVet)}</option>
            </select>
          </div>

          <div>
            <label htmlFor="reg-password" style={labelStyle}>{t(s.passwordLabel)}</label>
            <input id="reg-password" type="password" required autoComplete="new-password"
              minLength={8}
              value={password} onChange={e => setPassword(e.target.value)}
              style={inputStyle} />
          </div>

          {error && (
            <div role="alert" style={{
              padding: '10px 14px', background: 'var(--warn-bg)',
              border: '1px solid #f0a86d', borderRadius: 8,
              fontSize: 13, color: 'var(--warn)',
            }}>{error}</div>
          )}

          <button type="submit" disabled={loading} className="button"
            style={{
              width: '100%', justifyContent: 'center', minHeight: TOUCH_TARGET,
              opacity: loading ? 0.65 : 1,
            }}>
            {loading ? t(s.submitting) : t(s.submit)}
          </button>
        </form>

        <p className="muted" style={{ fontSize: 11, lineHeight: 1.6 }}>{t(s.pdpaNotice)}</p>

        <p style={{ textAlign: 'center', fontSize: 13 }}>
          <a href="/signin" style={{ color: 'var(--accent)' }}>{t(s.haveAccount)}</a>
        </p>
        <p className="muted" style={{ textAlign: 'center' }}>
          <a href="/" style={{ color: 'var(--accent)' }}>{t(s.backHome)}</a>
        </p>
      </div>
    </main>
  )
}
