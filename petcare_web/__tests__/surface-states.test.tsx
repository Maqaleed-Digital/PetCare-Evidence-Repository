/**
 * PORT-08 — empty / loading / error state coverage per surface.
 *
 * A surface has three states besides the happy one, and each fails differently
 * when it is missing:
 *
 *   EMPTY    nothing to show. Missing, the region renders blank and the user
 *            cannot tell "no records" from "still loading" from "broken" —
 *            or, worse, the surface fills the gap with placeholder rows that
 *            read as data.
 *   LOADING  a request is in flight. Missing, the form appears inert and gets
 *            submitted twice.
 *   ERROR    the request failed. Missing, the failure is silent and the user
 *            is left believing an action succeeded.
 *
 * The port source covered these per surface; the discipline ports, the code
 * does not — its surfaces are CRA routes with react-i18next, these are App
 * Router client components with `t({ar, en})`.
 *
 * The load-bearing half is the FORBIDDEN state, following PORT-01: it is not
 * enough that an empty state exists somewhere on the page, because a fabricated
 * row can sit happily beside it. The guards below name states that must not
 * appear.
 *
 * Authority: MVC-GOV-CANON-001 (controlled port from LEGACY_TO_PORT_FROM).
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LangProvider } from '@/components/LangProvider'

import OwnerPage from '@/app/owner/page'
import VetPage from '@/app/vet/page'
import PharmacyPage from '@/app/pharmacy/page'
import AccountPage from '@/app/account/page'
import SignInPage from '@/app/signin/page'
import RegisterPage from '@/app/register/page'
import RouteError from '@/app/error'
import { STRINGS } from '@/lib/strings'

const replaceMock = vi.fn()
vi.mock('next/navigation', () => ({
  useRouter: () => ({ replace: replaceMock, push: vi.fn() }),
  usePathname: () => '/',
}))

function mount(ui: React.ReactElement) {
  return render(<LangProvider>{ui}</LangProvider>)
}

beforeEach(() => {
  replaceMock.mockReset()
})

afterEach(() => {
  vi.restoreAllMocks()
})

// ---------------------------------------------------------------------------
// EMPTY — every surface that lists things says so when it lists nothing
// ---------------------------------------------------------------------------

describe('PORT-08 empty states', () => {
  it('/owner names an empty state for each of its list regions', () => {
    mount(<OwnerPage />)
    for (const key of ['petProfileEmpty', 'timelineEmpty', 'consentEmpty'] as const) {
      expect(
        screen.getByText(STRINGS.owner[key].ar),
        `/owner is missing the ${key} empty state`,
      ).toBeInTheDocument()
    }
  })

  it('/pharmacy names an empty state for every queue it shows', () => {
    mount(<PharmacyPage />)
    for (const empty of ['القائمة فارغة', 'لا توجد تنبيهات نشطة',
                         'لا توجد عناصر سلسلة باردة', 'لا توجد عمليات صرف بعد']) {
      expect(screen.getByText(empty)).toBeInTheDocument()
    }
  })

  it('/vet names an empty state for the consultation queue', () => {
    mount(<VetPage />)
    expect(screen.getByTestId('vet-queue-empty')).toBeInTheDocument()
  })

  it('/account says so when there is no signed-in identity', () => {
    mount(<AccountPage />)
    expect(screen.getByText(STRINGS.account.notSignedIn.ar)).toBeInTheDocument()
  })

  it('/account says so when the browser holds no consent record', () => {
    mount(<AccountPage />)
    expect(screen.getByText(STRINGS.consentState.noRecord.ar)).toBeInTheDocument()
  })
})

// ---------------------------------------------------------------------------
// FORBIDDEN — an empty surface must not manufacture rows that read as data
// ---------------------------------------------------------------------------

describe('PORT-08 forbidden states', () => {
  it('/vet does not present case rows while the queue is empty', () => {
    /*
     * The defect this closes: the vet queue rendered three table rows —
     * "Waiting", "Draft", "Pending" against an em-dash patient — with an
     * Open / Review & sign / Authorize action on each. There is no case
     * source in the pilot, so all three were fabricated. On a clinical
     * surface that is not cosmetic: "Prescription - Pending - Authorize"
     * reads as a prescription waiting on a veterinarian.
     */
    mount(<VetPage />)
    const forbidden = ['بانتظار', 'مسودة', 'معلّقة']
    for (const badge of forbidden) {
      expect(
        screen.queryByText(badge),
        `/vet renders the case-status badge "${badge}" with no case behind it`,
      ).not.toBeInTheDocument()
    }
    expect(screen.queryAllByRole('row')).toHaveLength(0)
  })

  it('/vet discloses that the queue is scaffolded rather than merely empty', () => {
    // "Empty" and "not built yet" are different claims and the pilot is the
    // second. WI-5's disclosure banner is the canonical way to say so.
    mount(<VetPage />)
    expect(screen.getByTestId('mode-disclosure-inline')).toBeInTheDocument()
  })

  it('no surface leaves a list region blank with neither rows nor an empty state', () => {
    /*
     * The generic form of the guard, and the one that survives new surfaces
     * being added: a region marked `data-list-region` must resolve to one of
     * the two legitimate outcomes — rows, or an explicit empty state. Neither
     * is the blank region this whole tranche exists to prevent.
     *
     * The inspected count is asserted at the end because a guard that iterates
     * over zero regions passes while checking nothing. If a surface drops its
     * markers, this fails on the denominator rather than going quiet.
     */
    let inspected = 0
    for (const [name, ui] of [
      ['/owner', <OwnerPage key="o" />],
      ['/vet', <VetPage key="v" />],
      ['/pharmacy', <PharmacyPage key="p" />],
    ] as const) {
      const { container, unmount } = mount(ui)
      const regions = container.querySelectorAll('[data-list-region]')
      expect(regions.length, `${name}: no list regions are marked`).toBeGreaterThan(0)
      for (const region of Array.from(regions)) {
        inspected += 1
        const hasRows = region.querySelectorAll('[data-list-row]').length > 0
        const hasEmpty = region.querySelector('[data-list-empty]') !== null
        expect(
          hasRows || hasEmpty,
          `${name}: list region "${region.getAttribute('data-list-region')}" ` +
          'resolved to neither rows nor an empty state',
        ).toBe(true)
      }
      unmount()
    }
    expect(inspected).toBe(8)
  })

  it('the list-region guard fails on a region that resolves to neither', () => {
    // Positive control. The guard above passes by finding nothing wrong, which
    // is what a guard reading the wrong attribute also does.
    const { container } = mount(
      <div data-list-region="control-blank" />,
    )
    const region = container.querySelector('[data-list-region]')!
    const hasRows = region.querySelectorAll('[data-list-row]').length > 0
    const hasEmpty = region.querySelector('[data-list-empty]') !== null
    expect(hasRows || hasEmpty).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// LOADING — a request in flight is visible and the control is not re-armed
// ---------------------------------------------------------------------------

function deferredFetch() {
  let release: (value: unknown) => void = () => {}
  const gate = new Promise((resolve) => { release = resolve })
  const spy = vi.spyOn(globalThis, 'fetch').mockImplementation(
    () => gate as unknown as Promise<Response>,
  )
  return { release, spy }
}

describe('PORT-08 loading states', () => {
  it('/signin shows the submitting label and disables submit while in flight', async () => {
    const { release } = deferredFetch()
    const user = userEvent.setup()
    mount(<SignInPage />)

    await user.type(screen.getByLabelText(/البريد الإلكتروني/), 'owner@test.com')
    await user.type(screen.getByLabelText(/كلمة المرور/), 'Pilot2026!')
    await user.click(screen.getByRole('button', { name: STRINGS.signin.submit.ar }))

    const button = await screen.findByRole('button', { name: STRINGS.signin.submitting.ar })
    expect(button).toBeDisabled()

    release({ ok: false, status: 500, json: async () => ({}) })
    await waitFor(() => expect(button).not.toBeDisabled())
  })

  it('/register shows the submitting label and disables submit while in flight', async () => {
    const { release } = deferredFetch()
    const user = userEvent.setup()
    mount(<RegisterPage />)

    await user.type(screen.getByLabelText(/الاسم الكامل/), 'Test Owner')
    await user.type(screen.getByLabelText(/البريد الإلكتروني/), 'owner@test.com')
    await user.type(screen.getByLabelText(/رمز الدعوة/), 'OWNER-PILOT-001')
    await user.type(screen.getByLabelText(/كلمة المرور/), 'Pilot2026!')
    await user.click(screen.getByRole('button', { name: STRINGS.register.submit.ar }))

    const button = await screen.findByRole('button', { name: STRINGS.register.submitting.ar })
    expect(button).toBeDisabled()

    release({ ok: false, status: 500, json: async () => ({}) })
    await waitFor(() => expect(button).not.toBeDisabled())
  })
})

// ---------------------------------------------------------------------------
// ERROR — every failure mode reaches the user, and the form recovers
// ---------------------------------------------------------------------------

describe('PORT-08 error states', () => {
  async function submitSignIn() {
    const user = userEvent.setup()
    mount(<SignInPage />)
    await user.type(screen.getByLabelText(/البريد الإلكتروني/), 'owner@test.com')
    await user.type(screen.getByLabelText(/كلمة المرور/), 'Pilot2026!')
    await user.click(screen.getByRole('button', { name: STRINGS.signin.submit.ar }))
  }

  it('/signin surfaces a network failure rather than failing silently', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new TypeError('Failed to fetch'))
    await submitSignIn()
    expect(await screen.findByText(STRINGS.signin.errNetwork.ar)).toBeInTheDocument()
    expect(replaceMock).not.toHaveBeenCalled()
  })

  it('/signin distinguishes rejected credentials from a server failure', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      { ok: false, status: 401, json: async () => ({}) } as Response,
    )
    await submitSignIn()
    expect(await screen.findByText(STRINGS.signin.errInvalid.ar)).toBeInTheDocument()
    expect(screen.queryByText(STRINGS.signin.errNetwork.ar)).not.toBeInTheDocument()
  })

  it('/signin re-arms the form after a failure instead of stranding it', async () => {
    // `finally { setLoading(false) }` is the whole reason this passes. Without
    // it a failed attempt leaves a permanently disabled button and the user has
    // to reload to try again.
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new TypeError('Failed to fetch'))
    await submitSignIn()
    await screen.findByText(STRINGS.signin.errNetwork.ar)
    expect(screen.getByRole('button', { name: STRINGS.signin.submit.ar })).toBeEnabled()
  })

  it('/register surfaces a network failure and does not navigate', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new TypeError('Failed to fetch'))
    const user = userEvent.setup()
    mount(<RegisterPage />)
    await user.type(screen.getByLabelText(/الاسم الكامل/), 'Test Owner')
    await user.type(screen.getByLabelText(/البريد الإلكتروني/), 'owner@test.com')
    await user.type(screen.getByLabelText(/رمز الدعوة/), 'OWNER-PILOT-001')
    await user.type(screen.getByLabelText(/كلمة المرور/), 'Pilot2026!')
    await user.click(screen.getByRole('button', { name: STRINGS.register.submit.ar }))

    expect(await screen.findByText(STRINGS.register.errNetwork.ar)).toBeInTheDocument()
    expect(replaceMock).not.toHaveBeenCalled()
  })

  it('a render failure lands on the boundary with a way out, not a blank page', () => {
    // PORT-03's boundary is the error state of last resort. Asserted here so
    // the three-state contract is complete on one page rather than split.
    const reset = vi.fn()
    mount(<RouteError error={Object.assign(new Error('boom'), { digest: 'd-1' })} reset={reset} />)
    expect(screen.getByTestId('route-error-boundary')).toBeInTheDocument()
    expect(screen.getByTestId('route-error-retry')).toBeInTheDocument()
    expect(screen.getByTestId('route-error-digest')).toHaveTextContent('d-1')
  })
})

// ---------------------------------------------------------------------------
// Vacuity guards
// ---------------------------------------------------------------------------

describe('PORT-08 guards are armed', () => {
  it('the surfaces under test actually render content', () => {
    // Every absence assertion above would pass against a component that
    // rendered nothing at all.
    for (const ui of [<OwnerPage key="o" />, <VetPage key="v" />, <PharmacyPage key="p" />]) {
      const { container, unmount } = mount(ui)
      expect(container.textContent?.trim().length ?? 0).toBeGreaterThan(200)
      unmount()
    }
  })

  it('the forbidden-badge query would find those badges if they were present', () => {
    // Positive control for the /vet guard: `queryByText` returning null is also
    // what a wrong query string returns. This proves the strings are findable.
    mount(
      <div>
        <span>بانتظار</span><span>مسودة</span><span>معلّقة</span>
      </div>,
    )
    for (const badge of ['بانتظار', 'مسودة', 'معلّقة']) {
      expect(screen.getByText(badge)).toBeInTheDocument()
    }
  })

  it('every error string asserted above is distinct, so the tests discriminate', () => {
    const strings = [
      STRINGS.signin.errNetwork.ar,
      STRINGS.signin.errInvalid.ar,
      STRINGS.register.errNetwork.ar,
    ]
    expect(new Set(strings).size).toBe(strings.length)
  })
})
