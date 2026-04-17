'use client'
import { usePathname, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'
import { LanguageToggle } from '@/components/LanguageToggle'
import { STRINGS } from '@/lib/strings'

type NavUser = { email: string; role: string; full_name: string }

export function Nav() {
  const path = usePathname()
  const router = useRouter()
  const { t } = useLang()
  const [user, setUser] = useState<NavUser | null>(null)
  const [checked, setChecked] = useState(false)

  useEffect(() => {
    const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
    fetch(`${apiBase}/api/auth/me`, { credentials: 'include' })
      .then(r => (r.ok ? r.json() : null))
      .then(data => setUser(data ?? null))
      .catch(() => setUser(null))
      .finally(() => setChecked(true))
  }, [])

  async function handleSignOut() {
    const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
    try {
      await fetch(`${apiBase}/api/auth/sign-out`, { method: 'POST', credentials: 'include' })
    } catch { /* ignore */ }
    document.cookie = 'petcare_role=; path=/; max-age=0'
    setUser(null)
    router.replace('/signin')
  }

  return (
    <nav className="nav">
      <a className="nav-brand" href="/">{t(STRINGS.nav.brand)}</a>
      <div className="nav-links">
        <a className={`nav-link${path === '/' ? ' active' : ''}`} href="/">
          {t(STRINGS.nav.home)}
        </a>
        <a className={`nav-link${path.startsWith('/onboarding') ? ' active' : ''}`} href="/onboarding">
          {t(STRINGS.nav.clinics)}
        </a>
      </div>
      <div className="nav-actions">
        <LanguageToggle />
        {!checked ? null : user ? (
          <>
            <span style={{ fontSize: 13, color: 'var(--text-muted, #666)', marginRight: 8 }}>
              {user.full_name || user.email}
              <span style={{ marginLeft: 6, fontSize: 11, background: 'var(--accent-bg, #e8f0fe)', color: 'var(--accent, #1a56db)', borderRadius: 4, padding: '1px 6px' }}>
                {user.role}
              </span>
            </span>
            <button
              className="button button-outline button-sm"
              onClick={handleSignOut}
            >
              {t(STRINGS.nav.signOut)}
            </button>
          </>
        ) : (
          <a className="button button-outline button-sm" href="/signin">
            {t(STRINGS.nav.signIn)}
          </a>
        )}
      </div>
    </nav>
  )
}
