'use client'
import { usePathname } from 'next/navigation'

export function Nav() {
  const path = usePathname()

  return (
    <nav className="nav">
      <a className="nav-brand" href="/">VetiCare</a>
      <div className="nav-links">
        <a className={`nav-link${path === '/' ? ' active' : ''}`} href="/">Home</a>
        <a className={`nav-link${path.startsWith('/onboarding') ? ' active' : ''}`} href="/onboarding">Clinics</a>
      </div>
      <div className="nav-actions">
        <a className="button button-outline button-sm" href="/signin">Sign in</a>
      </div>
    </nav>
  )
}
