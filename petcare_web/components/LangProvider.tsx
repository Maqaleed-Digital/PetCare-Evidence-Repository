'use client'

/**
 * LangProvider — lightweight React context for AR/EN switching.
 *
 * - Persists preference in localStorage ('vc_lang')
 * - Sets document.documentElement.lang + dir on every change
 * - Default: 'ar' (Arabic-first per FR-09)
 */
import {
  createContext, useContext, useEffect, useState, useCallback,
  type ReactNode,
} from 'react'
import type { Lang } from '@/lib/strings'

interface LangContextValue {
  lang: Lang
  toggle: () => void
  t: (strings: { ar: string; en: string }) => string
}

const LangContext = createContext<LangContextValue>({
  lang: 'ar',
  toggle: () => {},
  t: (s) => s.ar,
})

export function LangProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>('ar')

  // Hydrate from localStorage on first render (client-only)
  useEffect(() => {
    const stored = localStorage.getItem('vc_lang') as Lang | null
    const initial: Lang = stored === 'en' ? 'en' : 'ar'
    setLang(initial)
    document.documentElement.lang = initial
    document.documentElement.dir  = initial === 'ar' ? 'rtl' : 'ltr'
  }, [])

  const toggle = useCallback(() => {
    setLang(prev => {
      const next: Lang = prev === 'ar' ? 'en' : 'ar'
      localStorage.setItem('vc_lang', next)
      document.documentElement.lang = next
      document.documentElement.dir  = next === 'ar' ? 'rtl' : 'ltr'
      return next
    })
  }, [])

  const t = useCallback(
    (strings: { ar: string; en: string }) => strings[lang],
    [lang],
  )

  return (
    <LangContext.Provider value={{ lang, toggle, t }}>
      {children}
    </LangContext.Provider>
  )
}

export function useLang() {
  return useContext(LangContext)
}
