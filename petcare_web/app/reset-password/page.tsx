'use client'

/** /reset-password?token=… — set a new password (MVC-EPC-D-001 D2, J-O1). Every existing session is ended server-side. */
import { FormEvent, Suspense, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { Button, Field, Notice, Page, useCopy } from '@/components/ui'
import { AC } from '@/components/auth/AccountFlows'

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')

function Reset() {
  const { tr } = useCopy()
  const token = useSearchParams().get('token') ?? ''
  const [password, setPassword] = useState('')
  const [state, setState] = useState<'idle' | 'done' | 'bad' | 'short'>('idle')
  async function submit(e: FormEvent) {
    e.preventDefault()
    const pw = password
    setPassword('')
    try {
      const r = await fetch(`${apiBase}/api/auth/password-reset/confirm`, { method: 'POST',
        headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ token, password: pw }) })
      const err = r.ok ? '' : (await r.json().catch(() => ({})))?.detail?.error
      setState(r.ok ? 'done' : err === 'PASSWORD_TOO_SHORT' ? 'short' : 'bad')
    } catch { setState('bad') }
  }
  return (
    <Page title={AC.resetTitle} testId="reset-password">
      {state === 'done' ? (
        <Notice tone="success" testId="reset-done">{tr(AC.resetDone)} <a className="ds-link" href="/signin">{tr(AC.signIn)}</a></Notice>
      ) : (
        <form onSubmit={submit} className="ds-card">
          <Field label={AC.newPassword} hint={AC.passwordHint} type="password" minLength={10} value={password}
                 onChange={e => setPassword(e.currentTarget.value)} required autoComplete="new-password" />
          {state === 'bad' && <Notice tone="danger" testId="reset-bad">{tr(AC.linkInvalid)}</Notice>}
          {state === 'short' && <Notice tone="danger">{tr(AC.tooShort)}</Notice>}
          <Button type="submit">{tr(AC.save)}</Button>
        </form>
      )}
    </Page>
  )
}

export default function ResetPasswordPage() {
  return <Suspense><Reset /></Suspense>
}
