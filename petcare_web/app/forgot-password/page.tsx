'use client'

/** /forgot-password — request a reset link (MVC-EPC-D-001 D2, J-O1). Same answer for any address (no enumeration). */
import { FormEvent, useState } from 'react'
import { Button, Field, Notice, Page, useCopy } from '@/components/ui'
import { AC } from '@/components/auth/AccountFlows'

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')

export default function ForgotPasswordPage() {
  const { lang, tr } = useCopy()
  const [email, setEmail] = useState('')
  const [state, setState] = useState<'idle' | 'sent' | 'error'>('idle')
  async function submit(e: FormEvent) {
    e.preventDefault()
    try {
      const r = await fetch(`${apiBase}/api/auth/password-reset/request`, { method: 'POST',
        headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, locale: lang }) })
      setState(r.status === 202 ? 'sent' : 'error')
    } catch { setState('error') }
  }
  return (
    <Page title={AC.forgotTitle} testId="forgot-password">
      {state === 'sent' ? <Notice tone="success" testId="forgot-sent">{tr(AC.forgotSent)}</Notice> : (
        <form onSubmit={submit} className="ds-card">
          <p>{tr(AC.forgotIntro)}</p>
          <Field label={AC.email} type="email" value={email} onChange={e => setEmail(e.currentTarget.value)} required autoComplete="email" />
          {state === 'error' && <Notice tone="danger">{tr(AC.unavailable)}</Notice>}
          <Button type="submit">{tr(AC.send)}</Button>
        </form>
      )}
    </Page>
  )
}
