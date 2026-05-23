'use client'

/**
 * /account — Settings & rights surface (MVC-UX-WO-002 mount point).
 *
 * Hosts WI-2 PDPLRightsEntry and WI-3 ConsentStateView. Available to
 * any authenticated user (middleware gates on petcare_role).
 */

import { useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'
import { STRINGS } from '@/lib/strings'
import { PDPLRightsEntry } from '@/components/PDPLRightsEntry'
import { ConsentStateView } from '@/components/ConsentStateView'

interface VcUser {
  user_id: string
  email: string
  name: string
  role: string
}

export default function AccountPage() {
  const { t } = useLang()
  const s = STRINGS.account
  const [user, setUser] = useState<VcUser | null>(null)
  const [hydrated, setHydrated] = useState(false)

  useEffect(() => {
    if (typeof window === 'undefined') return
    const raw = localStorage.getItem('vc_user')
    if (raw) {
      try { setUser(JSON.parse(raw)) } catch { setUser(null) }
    }
    setHydrated(true)
  }, [])

  return (
    <main className="stack" style={{ maxWidth: 880 }}>
      <div>
        <div className="kicker">{t(s.kicker)}</div>
        <div className="title-lg">{t(s.title)}</div>
      </div>

      {hydrated && user ? (
        <div className="card card-sm" style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
          <div className="kicker" style={{ margin: 0 }}>{t(s.signedInAs)}</div>
          <div style={{ fontSize: 14, fontWeight: 600 }}>{user.name}</div>
          <span className="badge badge-blue">{user.role}</span>
        </div>
      ) : hydrated ? (
        <div className="note">
          <span className="muted">{t(s.notSignedIn)}</span>
        </div>
      ) : null}

      <PDPLRightsEntry />
      <ConsentStateView />

      <p>
        <a href="/owner" style={{ color: 'var(--accent)', fontSize: 14 }}>{t(s.backToOwner)}</a>
      </p>
    </main>
  )
}
