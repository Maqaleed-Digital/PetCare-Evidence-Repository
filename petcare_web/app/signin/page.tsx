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
        setError('البريد الإلكتروني أو كلمة المرور غير صحيحة.')
        return
      }
      if (res.status === 403) {
        setError('هذا الحساب غير نشط. تواصل مع المسؤول.')
        return
      }
      if (!res.ok) {
        setError(`فشل تسجيل الدخول (${res.status}). حاول مرة أخرى.`)
        return
      }

      const data = await res.json()
      const role: string = data?.user?.role ?? ''

      setRoleCookie(role)

      const dest = ROLE_REDIRECT[role] ?? '/'
      router.replace(dest)
    } catch {
      setError('تعذّر الوصول إلى الخادم. تحقق من اتصالك وحاول مرة أخرى.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main style={{ maxWidth: 480, margin: '80px auto', padding: '0 24px' }}>
      <div className="card stack" style={{ padding: 40 }}>

        <div>
          <div className="kicker">VetiCare</div>
          <div className="title-lg">تسجيل الدخول إلى حسابك</div>
          <p className="subtitle" style={{ marginTop: 6 }}>
            أدخل بياناتك للوصول إلى منصة VetiCare
          </p>
        </div>

        <form onSubmit={handleSubmit} className="stack" style={{ gap: 16 }}>
          <div>
            <label
              htmlFor="email"
              style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: 'var(--text)' }}
            >
              البريد الإلكتروني
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
              كلمة المرور
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
            {loading ? 'جارٍ تسجيل الدخول…' : 'تسجيل الدخول'}
          </button>
        </form>

        <p className="muted" style={{ textAlign: 'center', fontSize: 12 }}>
          لا يوجد تسجيل ذاتي. تواصل مع مسؤول التجريب للحصول على صلاحية الوصول.
        </p>

        <p className="muted" style={{ textAlign: 'center' }}>
          <a href="/" style={{ color: 'var(--accent)' }}>→ العودة للرئيسية</a>
        </p>
      </div>
    </main>
  )
}
