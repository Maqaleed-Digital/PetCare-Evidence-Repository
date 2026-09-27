'use client'

/**
 * Step-up prompt + hook (MVC-EPC-B-001 Lane B). `useStepUp()` gives a page `stepUpFetch(path, init)`, which sends the
 * request and, only when the SERVER answers with a step-up refusal, opens this dialog; after a successful step-up the
 * original request is sent once more (lib/stepUp.ts). The code typed here lives only in this component's state for the
 * duration of the request — never persisted, never logged — and is cleared after every submission.
 */

import { KeyboardEvent, ReactNode, useCallback, useEffect, useRef, useState } from 'react'
import { useLang } from '@/components/LangProvider'
import { SECURITY_PATH, STEP_UP_STRINGS as S, StepUpOutcome, withStepUp } from '@/lib/stepUp'

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
const send = (path: string, init?: RequestInit) =>
  fetch(`${apiBase}${path}`, { credentials: 'include', cache: 'no-store', ...init })

type Mode = 'totp' | 'recovery'

function StepUpDialog({ onDone }: { onDone: (ok: boolean) => void }) {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  const t = (k: keyof typeof S) => S[k][isAr ? 'ar' : 'en']
  const [mode, setMode] = useState<Mode>('totp')
  const [code, setCode] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const dialogRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => { inputRef.current?.focus() }, [mode])

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    const value = code
    setCode('')                                   // the code does not outlive the request
    setBusy(true)
    setError('')
    try {
      const r = await send(mode === 'totp' ? '/api/me/mfa/step-up' : '/api/me/mfa/recovery', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ code: value }),
      })
      if (r.ok) { onDone(true); return }
      setError(r.status === 401 ? t(mode === 'totp' ? 'invalidCode' : 'invalidRecovery') : t('unavailable'))
    } catch {
      setError(t('unavailable'))
    } finally {
      setBusy(false)
    }
  }

  function trapFocus(e: KeyboardEvent<HTMLDivElement>) {
    if (e.key === 'Escape') { e.preventDefault(); onDone(false); return }
    if (e.key !== 'Tab' || !dialogRef.current) return
    const items = Array.from(dialogRef.current.querySelectorAll<HTMLElement>('input, button:not([disabled])'))
    if (items.length === 0) return
    const first = items[0], last = items[items.length - 1]
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus() }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus() }
  }

  return (
    <div className="modal-backdrop" data-testid="step-up-backdrop">
      <div ref={dialogRef} role="dialog" aria-modal="true" aria-labelledby="step-up-title" aria-describedby="step-up-explain"
           dir={isAr ? 'rtl' : 'ltr'} className="card stack" data-testid="step-up-dialog" onKeyDown={trapFocus}>
        <h2 id="step-up-title" className="title-md">{t('title')}</h2>
        <p id="step-up-explain">{t('explain')}</p>
        <form onSubmit={submit} className="stack">
          <label htmlFor="step-up-code">{t(mode === 'totp' ? 'code' : 'recovery')}</label>
          <input id="step-up-code" ref={inputRef} name="step-up-code" value={code} autoComplete="one-time-code"
                 inputMode={mode === 'totp' ? 'numeric' : 'text'} aria-invalid={error ? true : undefined}
                 aria-describedby={error ? 'step-up-error' : undefined}
                 onChange={e => setCode(e.currentTarget.value)} required />
          {error && <p id="step-up-error" role="alert" data-testid="step-up-error">{error}</p>}
          <div className="row">
            <button type="submit" className="btn" disabled={busy || !code}>{t('verify')}</button>
            <button type="button" className="btn" onClick={() => onDone(false)}>{t('cancel')}</button>
          </div>
        </form>
        <button type="button" className="link" onClick={() => { setMode(mode === 'totp' ? 'recovery' : 'totp'); setCode(''); setError('') }}>
          {t(mode === 'totp' ? 'useRecovery' : 'useCode')}
        </button>
      </div>
    </div>
  )
}

/** Shown when the server refuses a sensitive operation pending (re-)enrolment — routes the user to enrolment. */
export function EnrolmentRequiredNotice() {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  return (
    <div role="alert" className="note" data-testid="enrolment-required" dir={isAr ? 'rtl' : 'ltr'}>
      <p>{S.enrolmentRequired[isAr ? 'ar' : 'en']}</p>
      <a href={SECURITY_PATH} className="btn">{S.goEnrol[isAr ? 'ar' : 'en']}</a>
    </div>
  )
}

export function useStepUp(): {
  stepUpFetch: (path: string, init?: RequestInit) => Promise<StepUpOutcome>
  stepUpUi: ReactNode
} {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  const [open, setOpen] = useState(false)
  const [notice, setNotice] = useState<'none' | 'enrol' | 'failed'>('none')
  const resolver = useRef<((ok: boolean) => void) | null>(null)

  const prompt = useCallback(() => new Promise<boolean>(resolve => {
    resolver.current = resolve
    setOpen(true)
  }), [])

  const done = useCallback((ok: boolean) => {
    setOpen(false)
    const r = resolver.current
    resolver.current = null
    r?.(ok)
  }, [])

  const stepUpFetch = useCallback(async (path: string, init?: RequestInit) => {
    setNotice('none')
    const outcome = await withStepUp(() => send(path, init), prompt)
    if (outcome.state === 'enrolment_required') setNotice('enrol')
    if (outcome.state === 'step_up_failed') setNotice('failed')
    return outcome
  }, [prompt])

  const stepUpUi = (
    <>
      {open && <StepUpDialog onDone={done} />}
      {notice === 'enrol' && <EnrolmentRequiredNotice />}
      {notice === 'failed' && (
        <p role="alert" data-testid="step-up-still-required" dir={isAr ? 'rtl' : 'ltr'}>
          {S.stillRequired[isAr ? 'ar' : 'en']}
        </p>
      )}
    </>
  )
  return { stepUpFetch, stepUpUi }
}
