'use client'

/**
 * error.tsx — route-segment error boundary.
 *
 * A render error must cost one screen, not the application. Without this file
 * Next.js has no boundary beneath the root layout, so a single bad payload on
 * one page unmounts the tree and leaves the user a blank page rather than a
 * failed panel with a way out.
 *
 * Ported from the validated petcare-platform serving layer, where exactly that
 * failure was observed: an admin surface threw on an unexpected API shape and
 * blanked the whole app. The behaviour is ported, not the code — that
 * implementation was a CRA class component; this is the App Router convention.
 *
 * Authority: MVC-GOV-CANON-001 (controlled port from LEGACY_TO_PORT_FROM).
 */
import { useEffect } from 'react'
import { useLang } from '@/components/LangProvider'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  const { t } = useLang()

  useEffect(() => {
    // Left visible deliberately: there is no client telemetry sink in this
    // build, and swallowing the error entirely would hide the failure.
    console.error('Unhandled render error', error)
  }, [error])

  return (
    <main
      role="alert"
      data-testid="route-error-boundary"
      style={{ padding: '2rem', maxWidth: 640, margin: '0 auto' }}
    >
      <h1 className="title-lg" style={{ marginBottom: '0.5rem' }}>
        {t({ ar: 'حدث خطأ', en: 'Something went wrong' })}
      </h1>
      <p style={{ marginBottom: '1rem' }}>
        {t({
          ar: 'تعذّر عرض هذه الصفحة. بياناتك لم تتأثر.',
          en: 'This page could not be displayed. Your data is unaffected.',
        })}
      </p>
      {error.digest && (
        <p
          data-testid="route-error-digest"
          style={{ fontFamily: 'monospace', fontSize: 12, opacity: 0.6 }}
        >
          {error.digest}
        </p>
      )}
      <button
        type="button"
        onClick={reset}
        data-testid="route-error-retry"
        style={{
          padding: '8px 16px',
          borderRadius: 8,
          border: '1.5px solid var(--vc-primary, #0F5E6E)',
          background: 'transparent',
          color: 'var(--vc-primary, #0F5E6E)',
          fontWeight: 700,
          cursor: 'pointer',
        }}
      >
        {t({ ar: 'إعادة المحاولة', en: 'Try again' })}
      </button>
    </main>
  )
}
