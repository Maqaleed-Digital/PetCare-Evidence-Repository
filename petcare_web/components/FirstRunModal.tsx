'use client'

/**
 * FirstRunModal — pilot guided first-run for newly-registered owners (WI-4).
 *
 * - Reuses the step-badge visual pattern from app/onboarding/page.tsx for
 *   visual consistency with clinic onboarding.
 * - AR-first via LangProvider.
 * - SKIPPABLE: skip button, backdrop click, and Esc all dismiss; completion
 *   is non-blocking (the portal is fully usable behind the modal once
 *   dismissed).
 * - Persistence: a single localStorage flag `vc_firstrun_done`. Once set,
 *   the modal does not re-mount. No telemetry, no retention loop, no
 *   engagement metrics — first-run only.
 */

import { useEffect, useState, useCallback } from 'react'
import { useLang } from '@/components/LangProvider'
import { STRINGS } from '@/lib/strings'
import { AdvisoryDisclosureBanner } from '@/components/AdvisoryDisclosureBanner'

const FLAG_KEY = 'vc_firstrun_done'
const TOTAL_STEPS = 3

export function FirstRunModal() {
  const { t } = useLang()
  const s = STRINGS.firstRun
  const [open, setOpen] = useState(false)
  const [step, setStep] = useState(0)

  useEffect(() => {
    if (typeof window === 'undefined') return
    if (!localStorage.getItem(FLAG_KEY)) setOpen(true)
  }, [])

  const close = useCallback((markDone: boolean) => {
    if (markDone) localStorage.setItem(FLAG_KEY, 'true')
    setOpen(false)
  }, [])

  useEffect(() => {
    if (!open) return
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') close(false)
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [open, close])

  if (!open) return null

  const stepCopy = [
    { badge: t(s.step1Badge), title: t(s.step1Title), body: t(s.step1Body) },
    { badge: t(s.step2Badge), title: t(s.step2Title), body: t(s.step2Body) },
    { badge: t(s.step3Badge), title: t(s.step3Title), body: t(s.step3Body) },
  ][step]

  const isLast = step === TOTAL_STEPS - 1

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="firstrun-title"
      onClick={(e) => { if (e.target === e.currentTarget) close(false) }}
      style={{
        position: 'fixed', inset: 0,
        background: 'rgba(16, 24, 40, 0.55)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: 16, zIndex: 50,
      }}
    >
      <div className="card stack" style={{
        maxWidth: 480, width: '100%', padding: 28, background: '#fff',
      }}>
        <div>
          <div className="kicker">{t(s.welcomeKicker)}</div>
          <div id="firstrun-title" className="title-lg">{t(s.welcomeTitle)}</div>
          <p className="subtitle" style={{ marginTop: 6 }}>{t(s.welcomeSub)}</p>
        </div>

        {/* WI-1 (MVC-UX-WO-002): advisory disclosure inside the first-run
            so owners see the "guidance, not clinical decision" framing
            before stepping through. */}
        <AdvisoryDisclosureBanner storageKey="vc_advisory_dismissed_firstrun" />

        <div className="card-sm card" style={{ borderColor: 'var(--accent-light)' }}>
          <span className="badge badge-blue" style={{ marginBottom: 10 }}>{stepCopy.badge}</span>
          <div className="title" style={{ fontSize: 16, marginBottom: 6 }}>{stepCopy.title}</div>
          <p className="subtitle">{stepCopy.body}</p>
        </div>

        {/* Step indicator dots — reuses the step pattern from /onboarding */}
        <div role="status" aria-label={`step ${step + 1} of ${TOTAL_STEPS}`}
          style={{ display: 'flex', gap: 6, justifyContent: 'center' }}>
          {Array.from({ length: TOTAL_STEPS }).map((_, i) => (
            <span key={i} style={{
              width: 8, height: 8, borderRadius: 999,
              background: i === step ? 'var(--accent)' : 'var(--line)',
            }} />
          ))}
        </div>

        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', justifyContent: 'space-between' }}>
          <button
            type="button"
            onClick={() => close(true)}
            className="button button-outline"
            style={{ minHeight: 48 }}
          >
            {t(s.skip)}
          </button>

          {isLast ? (
            <a
              href="/owner#pets"
              onClick={() => close(true)}
              className="button"
              style={{ minHeight: 48 }}
            >
              {t(s.primaryActionCta)}
            </a>
          ) : (
            <button
              type="button"
              onClick={() => setStep(step + 1)}
              className="button"
              style={{ minHeight: 48 }}
            >
              {t(s.next)}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
