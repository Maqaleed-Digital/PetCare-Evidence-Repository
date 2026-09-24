'use client'

import { useLang } from '@/components/LangProvider'

/**
 * LanguageToggle — teal pill showing current language with one-click swap.
 * Renders "AR" when Arabic is active, "EN" when English is active.
 * RTL-aware: positioned correctly in both directions via CSS.
 */
/**
 * FR-09 (U3): when a user is signed in, the new choice is also stored
 * server-side (PUT /api/me/preferences/language) so it survives a new session
 * on any device. Fire-and-forget: a failed save never blocks the switch.
 */
function persistLanguage(next: 'ar' | 'en') {
  if (typeof window === 'undefined' || !localStorage.getItem('vc_user')) return
  const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
  void fetch(`${apiBase}/api/me/preferences/language`, {
    method: 'PUT',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ language: next }),
  }).catch(() => undefined)
}

export function LanguageToggle() {
  const { lang, toggle } = useLang()

  return (
    <button
      onClick={() => { persistLanguage(lang === 'ar' ? 'en' : 'ar'); toggle() }}
      aria-label={lang === 'ar' ? 'Switch to English' : 'التبديل إلى العربية'}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 4,
        padding: '4px 12px',
        borderRadius: 999,
        border: '1.5px solid var(--vc-primary, #0F5E6E)',
        background: 'transparent',
        color: 'var(--vc-primary, #0F5E6E)',
        fontSize: 12,
        fontWeight: 700,
        letterSpacing: '0.06em',
        cursor: 'pointer',
        transition: 'background 0.15s, color 0.15s',
        fontFamily: 'var(--font-body)',
      }}
      onMouseEnter={e => {
        const el = e.currentTarget
        el.style.background = 'var(--vc-primary, #0F5E6E)'
        el.style.color = '#fff'
      }}
      onMouseLeave={e => {
        const el = e.currentTarget
        el.style.background = 'transparent'
        el.style.color = 'var(--vc-primary, #0F5E6E)'
      }}
    >
      <span style={{ opacity: lang === 'ar' ? 0.45 : 1 }}>EN</span>
      <span style={{ color: 'var(--vc-secondary, #7BAF9E)', fontWeight: 400 }}>/</span>
      <span style={{ opacity: lang === 'ar' ? 1 : 0.45 }}>AR</span>
    </button>
  )
}
