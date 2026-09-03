'use client'

/**
 * global-error.tsx — boundary of last resort.
 *
 * `app/error.tsx` sits inside the root layout, so it cannot catch a throw in
 * the layout itself. This file replaces the whole document when that happens,
 * which is why it renders its own <html> and <body>.
 *
 * It cannot use LangProvider — it replaces the layout that supplies it — so the
 * copy is static. Arabic leads, per FR-09, and the document carries lang/dir
 * explicitly because the layout that would have set them did not run.
 *
 * Authority: MVC-GOV-CANON-001 (controlled port from LEGACY_TO_PORT_FROM).
 */
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <html lang="ar" dir="rtl">
      <body>
        <main
          role="alert"
          data-testid="global-error-boundary"
          style={{
            padding: '2rem',
            maxWidth: 640,
            margin: '0 auto',
            fontFamily: 'system-ui, sans-serif',
          }}
        >
          <h1 style={{ marginBottom: '0.5rem' }}>حدث خطأ غير متوقع</h1>
          <p style={{ marginBottom: '0.25rem' }}>
            تعذّر تحميل التطبيق. بياناتك لم تتأثر.
          </p>
          <p style={{ marginBottom: '1rem', opacity: 0.7 }}>
            The application could not be loaded. Your data is unaffected.
          </p>
          {error.digest && (
            <p style={{ fontFamily: 'monospace', fontSize: 12, opacity: 0.6 }}>
              {error.digest}
            </p>
          )}
          <button
            type="button"
            onClick={reset}
            data-testid="global-error-retry"
            style={{
              padding: '8px 16px',
              borderRadius: 8,
              border: '1.5px solid #0F5E6E',
              background: 'transparent',
              color: '#0F5E6E',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            إعادة المحاولة / Try again
          </button>
        </main>
      </body>
    </html>
  )
}
