'use client'
import { usePathname, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'
import { LanguageToggle } from '@/components/LanguageToggle'
import { STRINGS } from '@/lib/strings'

export function Nav() {
  const path = usePathname()
  const router = useRouter()
  const { t } = useLang()
  const [user, setUser] = useState<{ name: string; role: string } | null>(null)
  const [checked, setChecked] = useState(false)

  useEffect(() => {
    if (typeof window === 'undefined') return
    const read = () => {
      const raw = localStorage.getItem('vc_user')
      if (raw) {
        try { setUser(JSON.parse(raw)) } catch { setUser(null) }
      } else {
        setUser(null)
      }
      setChecked(true)
    }
    read()
    window.addEventListener('vc_user_changed', read)
    window.addEventListener('storage', read)
    return () => {
      window.removeEventListener('vc_user_changed', read)
      window.removeEventListener('storage', read)
    }
  }, [])

  async function handleSignOut() {
    const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
    try {
      await fetch(`${apiBase}/api/auth/sign-out`, { method: 'POST', credentials: 'include' })
    } catch { /* ignore */ }
    document.cookie = 'petcare_role=; path=/; max-age=0'
    localStorage.removeItem('vc_user')
    window.dispatchEvent(new Event('vc_user_changed'))
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
              {user.name}
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
