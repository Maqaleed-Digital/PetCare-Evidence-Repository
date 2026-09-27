'use client'

/**
 * MyVetiCare design-system primitives (MVC-EPC-D-001 Lane D, D0 — gate G1). Every new screen composes these; styling
 * lives in app/design-system.css (tokens + logical properties, so RTL mirrors automatically). Every screen renders
 * one of the four data states (G4 / X4): <LoadingState>, <EmptyState>, <ErrorState>, <OfflineState>, or its content.
 * All copy is passed in by the screen as { ar, en } pairs; nothing here holds an untranslated string.
 */

import { ReactNode, useEffect, useId, useState } from 'react'
import { useLang } from '@/components/LangProvider'

export type Copy = { ar: string; en: string }
export const useCopy = () => {
  const { lang } = useLang()
  return { lang, isAr: lang === 'ar', tr: (c: Copy) => c[lang === 'ar' ? 'ar' : 'en'] }
}

export function Page({ kicker, title, children, testId }: { kicker?: Copy; title: Copy; children: ReactNode; testId?: string }) {
  const { isAr, tr } = useCopy()
  return (
    <main className="ds-page" dir={isAr ? 'rtl' : 'ltr'} data-testid={testId} data-ds="page">
      <header>
        {kicker && <div className="ds-page__kicker">{tr(kicker)}</div>}
        <h1 className="ds-page__title">{tr(title)}</h1>
      </header>
      {children}
    </main>
  )
}

export function Card({ title, children, testId }: { title?: Copy; children: ReactNode; testId?: string }) {
  const { tr } = useCopy()
  const id = useId()
  return (
    <section className="ds-card" aria-labelledby={title ? id : undefined} data-testid={testId}>
      {title && <h2 id={id} className="title-md">{tr(title)}</h2>}
      {children}
    </section>
  )
}

export function Button({ children, variant = 'primary', ...rest }:
  React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' | 'danger' }) {
  const cls = `ds-btn${variant === 'primary' ? '' : ` ds-btn--${variant}`}`
  return <button type="button" {...rest} className={`${cls} ${rest.className ?? ''}`.trim()}>{children}</button>
}

export function Field({ label, hint, error, ...input }:
  React.InputHTMLAttributes<HTMLInputElement> & { label: Copy; hint?: Copy; error?: string }) {
  const { tr } = useCopy()
  const id = useId()
  const describedBy = [hint ? `${id}-hint` : '', error ? `${id}-error` : ''].filter(Boolean).join(' ') || undefined
  return (
    <div className="ds-field">
      <label className="ds-label" htmlFor={id}>{tr(label)}</label>
      <input id={id} className="ds-input" aria-invalid={error ? true : undefined} aria-describedby={describedBy} {...input} />
      {hint && <span id={`${id}-hint`} className="ds-hint">{tr(hint)}</span>}
      {error && <span id={`${id}-error`} className="ds-error-text" role="alert">{error}</span>}
    </div>
  )
}

export function Notice({ tone = 'info', children, testId }: { tone?: 'info' | 'success' | 'warn' | 'danger'; children: ReactNode; testId?: string }) {
  return <div className={`ds-notice ds-notice--${tone}`} role={tone === 'danger' ? 'alert' : 'status'} data-testid={testId}>{children}</div>
}

const STATE = {
  loading: { ar: 'جارٍ التحميل…', en: 'Loading…' },
  empty: { ar: 'لا توجد عناصر بعد.', en: 'Nothing here yet.' },
  error: { ar: 'تعذر تحميل البيانات.', en: 'The data could not be loaded.' },
  retry: { ar: 'إعادة المحاولة', en: 'Try again' },
  offline: { ar: 'أنت غير متصل بالإنترنت. ستُحدَّث البيانات عند عودة الاتصال.', en: 'You are offline. Data will refresh when you reconnect.' },
}

export function LoadingState({ label }: { label?: Copy }) {
  const { tr } = useCopy()
  return <div className="ds-state" role="status" aria-busy="true" data-state="loading"><div className="ds-spinner" aria-hidden="true" />{tr(label ?? STATE.loading)}</div>
}
export function EmptyState({ message, action }: { message?: Copy; action?: ReactNode }) {
  const { tr } = useCopy()
  return <div className="ds-state" role="status" data-state="empty"><p>{tr(message ?? STATE.empty)}</p>{action}</div>
}
export function ErrorState({ message, onRetry }: { message?: Copy; onRetry?: () => void }) {
  const { tr } = useCopy()
  return (
    <div className="ds-state" role="alert" data-state="error">
      <p>{tr(message ?? STATE.error)}</p>
      {onRetry && <Button variant="secondary" onClick={onRetry}>{tr(STATE.retry)}</Button>}
    </div>
  )
}
export function OfflineState() {
  const { tr } = useCopy()
  return <div className="ds-notice ds-notice--warn" role="status" data-state="offline">{tr(STATE.offline)}</div>
}

/** Browser connectivity, for the offline state every screen shows (G4). */
export function useOnline(): boolean {
  const [online, setOnline] = useState(true)
  useEffect(() => {
    const update = () => setOnline(navigator.onLine)
    update()
    window.addEventListener('online', update)
    window.addEventListener('offline', update)
    return () => { window.removeEventListener('online', update); window.removeEventListener('offline', update) }
  }, [])
  return online
}

/** The four data states in one place: a screen passes its load status and renders its content only when ready. */
export function DataView<T>({ status, data, onRetry, empty, children }: {
  status: 'loading' | 'error' | 'ready'; data: T | null; onRetry?: () => void; empty?: Copy
  children: (data: T) => ReactNode
}) {
  const online = useOnline()
  return (
    <>
      {!online && <OfflineState />}
      {status === 'loading' && <LoadingState />}
      {status === 'error' && <ErrorState onRetry={onRetry} />}
      {status === 'ready' && (data == null || (Array.isArray(data) && data.length === 0)
        ? <EmptyState message={empty} />
        : children(data as T))}
    </>
  )
}
