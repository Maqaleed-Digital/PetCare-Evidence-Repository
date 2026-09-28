'use client'

/** /verify-email?token=… — confirms an owner's address (MVC-EPC-D-001 D2, J-O1). The token is sent once, never stored. */
import { Suspense, useEffect, useRef, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { Notice, Page, useCopy } from '@/components/ui'
import { AC } from '@/components/auth/AccountFlows'

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')

function Verify() {
  const { tr } = useCopy()
  const token = useSearchParams().get('token') ?? ''
  const [state, setState] = useState<'busy' | 'ok' | 'bad'>('busy')
  const sent = useRef(false)
  useEffect(() => {
    if (sent.current) return
    sent.current = true
    if (!token) { setState('bad'); return }
    fetch(`${apiBase}/api/auth/verify-email`, { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token }) }).then(r => setState(r.ok ? 'ok' : 'bad')).catch(() => setState('bad'))
  }, [token])
  return (
    <Page title={AC.verifyTitle} testId="verify-email">
      {state === 'busy' && <Notice>{tr(AC.verifying)}</Notice>}
      {state === 'ok' && <Notice tone="success" testId="verify-ok">{tr(AC.verified)} <a className="ds-link" href="/signin">{tr(AC.signIn)}</a></Notice>}
      {state === 'bad' && <Notice tone="danger" testId="verify-bad">{tr(AC.linkInvalid)}</Notice>}
    </Page>
  )
}

export default function VerifyEmailPage() {
  return <Suspense><Verify /></Suspense>
}
