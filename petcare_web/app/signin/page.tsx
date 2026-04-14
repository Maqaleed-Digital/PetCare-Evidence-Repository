'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'

// Role → destination route mapping (aligned to middleware protectedRoutes)
const ROLE_REDIRECT: Record<string, string> = {
  platform_admin: '/admin',
  clinic_admin: '/admin',
  veterinarian: '/vet',
  owner: '/owner',
}

function setRoleCookie(role: string) {
  // Non-HttpOnly so Next.js middleware can read it for routing.
  // The HttpOnly petcare_pilot_session cookie (set by backend) is the real auth token.
  const maxAge = 60 * 60 * 12 // 12 h, matches backend session
  document.cookie = `petcare_role=${encodeURIComponent(role)}; path=/; max-age=${maxAge}; samesite=lax`
}

export default function SignInPage() {
  const router = useRouter()
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

      if (res.status === 401) {
        setError('Invalid email or password.')
        return
      }
      if (res.status === 403) {
        setError('This account is inactive. Contact your administrator.')
        return
      }
      if (!res.ok) {
        setError(`Sign-in failed (${res.status}). Try again.`)
        return
      }

      const data = await res.json()
      const role: string = data?.user?.role ?? ''

      setRoleCookie(role)

      const dest = ROLE_REDIRECT[role] ?? '/'
      router.replace(dest)
    } catch {
      setError('Could not reach the server. Check your connection and try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main style={{ maxWidth: 480, margin: '80px auto', padding: '0 24px' }}>
      <div className="card stack" style={{ padding: 40 }}>

        <div>
          <div className="kicker">MyVetiCare</div>
          <div className="title-lg">Sign in to your PetCare account</div>
          <p className="subtitle" style={{ marginTop: 6 }}>
            تسجيل الدخول إلى منصة ماي فيتيكير
          </p>
        </div>

        <form onSubmit={handleSubmit} className="stack" style={{ gap: 16 }}>
          <div>
            <label
              htmlFor="email"
              style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: 'var(--text)' }}
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={e => setEmail(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 12px',
                border: '1px solid var(--line)',
                borderRadius: 8,
                fontSize: 14,
                outline: 'none',
                background: '#fff',
              }}
            />
          </div>

          <div>
            <label
              htmlFor="password"
              style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: 'var(--text)' }}
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={e => setPassword(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 12px',
                border: '1px solid var(--line)',
                borderRadius: 8,
                fontSize: 14,
                outline: 'none',
                background: '#fff',
              }}
            />
          </div>

          {error && (
            <div
              style={{
                padding: '10px 14px',
                background: 'var(--warn-bg)',
                border: '1px solid #f0a86d',
                borderRadius: 8,
                fontSize: 13,
                color: 'var(--warn)',
              }}
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="button"
            style={{ width: '100%', justifyContent: 'center', opacity: loading ? 0.65 : 1 }}
          >
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <p className="muted" style={{ textAlign: 'center', fontSize: 12 }}>
          No self-registration. Contact your pilot administrator for access.
        </p>

        <p className="muted" style={{ textAlign: 'center' }}>
          <a href="/" style={{ color: 'var(--accent)' }}>← Back to home</a>
        </p>
      </div>
    </main>
  )
}
