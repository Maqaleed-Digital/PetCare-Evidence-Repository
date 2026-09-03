/**
 * Error boundaries — a render error must cost one screen, not the application.
 *
 * Ported behaviour, not ported code: the petcare-platform serving layer showed
 * that an admin surface throwing on an unexpected API shape unmounted the whole
 * tree and left a blank page. Next.js supplies the boundary as a route
 * convention, so these assert the convention is actually present and that what
 * it renders is Arabic-first and recoverable.
 *
 * Authority: MVC-GOV-CANON-001 (controlled port from LEGACY_TO_PORT_FROM).
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import ErrorBoundary from '@/app/error'
import GlobalError from '@/app/global-error'
import { LangProvider } from '@/components/LangProvider'

function makeError(digest?: string) {
  const error = new Error('boom') as Error & { digest?: string }
  if (digest) error.digest = digest
  return error
}

describe('route error boundary', () => {
  it('renders Arabic-first and does not leak the raw message', async () => {
    const reset = vi.fn()
    render(
      <LangProvider>
        <ErrorBoundary error={makeError()} reset={reset} />
      </LangProvider>,
    )

    expect(screen.getByTestId('route-error-boundary')).toBeInTheDocument()
    expect(screen.getByRole('alert')).toBeInTheDocument()
    expect(screen.getByText('حدث خطأ')).toBeInTheDocument()

    // A stack or raw throw message is not something to show a pet owner.
    expect(screen.queryByText(/boom/)).not.toBeInTheDocument()
  })

  it('offers a recovery action that calls reset', async () => {
    const reset = vi.fn()
    render(
      <LangProvider>
        <ErrorBoundary error={makeError()} reset={reset} />
      </LangProvider>,
    )

    await userEvent.click(screen.getByTestId('route-error-retry'))
    expect(reset).toHaveBeenCalledTimes(1)
  })

  it('surfaces the digest when Next supplies one', () => {
    render(
      <LangProvider>
        <ErrorBoundary error={makeError('abc123')} reset={vi.fn()} />
      </LangProvider>,
    )
    expect(screen.getByTestId('route-error-digest')).toHaveTextContent('abc123')
  })

  it('omits the digest node when there is none to show', () => {
    render(
      <LangProvider>
        <ErrorBoundary error={makeError()} reset={vi.fn()} />
      </LangProvider>,
    )
    expect(screen.queryByTestId('route-error-digest')).not.toBeInTheDocument()
  })
})

describe('global error boundary', () => {
  // This one replaces the root layout, so it cannot use LangProvider and must
  // carry lang/dir itself — the layout that would have set them did not run.
  it('renders without a language provider and stays recoverable', async () => {
    const reset = vi.fn()
    render(<GlobalError error={makeError()} reset={reset} />)

    expect(screen.getByTestId('global-error-boundary')).toBeInTheDocument()
    expect(screen.getByText('حدث خطأ غير متوقع')).toBeInTheDocument()

    await userEvent.click(screen.getByTestId('global-error-retry'))
    expect(reset).toHaveBeenCalledTimes(1)
  })
})
