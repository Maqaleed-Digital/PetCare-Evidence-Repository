import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, cleanup, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LangProvider } from '@/components/LangProvider'
import { LanguageToggle } from '@/components/LanguageToggle'
import SignInPage from '@/app/signin/page'

/**
 * FR-09 multi-language — ratified AC-FR-09-01 (every customer-facing surface in
 * Arabic, the default, and English) and AC-FR-09-02 (RTL on every customer-facing
 * page; the chosen language survives a new session). MVC-BUILD-RUNNER-001 U3.
 *
 * CUSTOMER-FACING = every page an owner, veterinarian or pharmacy/clinic user can
 * reach. /admin is the platform-operator console and is excluded (recorded in the
 * U3 receipt). The only Latin text allowed in Arabic mode is brand names and
 * e-mail addresses.
 */

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/',
}))

const CUSTOMER_PAGES: Record<string, () => Promise<{ default: () => JSX.Element }>> = {
  '/': () => import('@/app/page'),
  '/signin': () => import('@/app/signin/page'),
  '/register': () => import('@/app/register/page'),
  '/account': () => import('@/app/account/page'),
  '/onboarding': () => import('@/app/onboarding/page'),
  '/onboarding/pharmacy': () => import('@/app/onboarding/pharmacy/page'),
  '/owner': () => import('@/app/owner/page'),
  '/owner/emergency': () => import('@/app/owner/emergency/page'),
  '/owner/pets': () => import('@/app/owner/pets/page'),
  '/pharmacy': () => import('@/app/pharmacy/page'),
  '/privacy': () => import('@/app/privacy/page'),
  '/unauthorized': () => import('@/app/unauthorized/page'),
  '/vet': () => import('@/app/vet/page'),
}

const ALLOWED_LATIN = /^(?:My)?VetiCare$|^Maqaleed Vet by VetiCare$|^[\w.+-]+@[\w.-]+$/

function json(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}

function englishOnlyText(root: HTMLElement): string[] {
  const out: string[] = []
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT)
  let n: Node | null
  while ((n = w.nextNode())) {
    const t = (n.textContent ?? '').trim()
    if (/[A-Za-z]{3,}/.test(t) && !/[؀-ۿ]/.test(t) && !ALLOWED_LATIN.test(t)) out.push(t)
  }
  return out
}

beforeEach(() => {
  vi.restoreAllMocks()
  localStorage.clear()
  vi.stubGlobal('fetch', vi.fn(() => json([])))
})

describe('FR-09 — Arabic primary on every customer-facing page', () => {
  for (const [route, load] of Object.entries(CUSTOMER_PAGES)) {
    it(`${route}: Arabic by default, RTL, no English-only text`, async () => {
      const Page = (await load()).default
      const { container } = render(<LangProvider><Page /></LangProvider>)
      await waitFor(() => expect(document.documentElement.dir).toBe('rtl'))
      expect(document.documentElement.lang).toBe('ar')
      expect(englishOnlyText(container)).toEqual([])
      // A page must not override the document's RTL with its own LTR block.
      const ltr = [...container.querySelectorAll('[dir]')].filter(e => e.getAttribute('dir') === 'ltr')
      expect(ltr.map(e => e.tagName)).toEqual([])
      cleanup()
    })

    it(`${route}: English available and LTR when chosen`, async () => {
      localStorage.setItem('vc_lang', 'en')
      const Page = (await load()).default
      render(<LangProvider><Page /></LangProvider>)
      await waitFor(() => expect(document.documentElement.dir).toBe('ltr'))
      expect(document.documentElement.lang).toBe('en')
      cleanup()
    })
  }
})

describe('FR-09 — the chosen language survives a new session', () => {
  it('toggle stores the choice server-side when signed in', async () => {
    localStorage.setItem('vc_user', JSON.stringify({ user_id: 'u-1' }))
    const fetchMock = vi.fn((_url: string, _init?: RequestInit) => json({ language: 'en', source: 'stored' }))
    vi.stubGlobal('fetch', fetchMock)
    render(<LangProvider><LanguageToggle /></LangProvider>)
    await userEvent.setup().click(screen.getByRole('button'))
    const put = fetchMock.mock.calls.find(([, init]) => init?.method === 'PUT')
    expect(put).toBeTruthy()
    expect(String(put![0]).endsWith('/api/me/preferences/language')).toBe(true)
    expect(JSON.parse(String(put![1]!.body))).toEqual({ language: 'en' })
  })

  it('toggle does not call the server when signed out', async () => {
    const fetchMock = vi.fn(() => json({}))
    vi.stubGlobal('fetch', fetchMock)
    render(<LangProvider><LanguageToggle /></LangProvider>)
    await userEvent.setup().click(screen.getByRole('button'))
    expect(fetchMock).not.toHaveBeenCalled()
    expect(localStorage.getItem('vc_lang')).toBe('en')
  })

  it('sign-in restores the language stored in an earlier session', async () => {
    vi.stubGlobal('fetch', vi.fn((url: string) => {
      if (String(url).endsWith('/api/auth/sign-in')) {
        return json({ user: { user_id: 'u-1', email: 'o@x.test', full_name: 'O', role: 'owner' } })
      }
      if (String(url).endsWith('/api/me/preferences/language')) return json({ language: 'en', source: 'stored' })
      return json({})
    }))
    render(<LangProvider><SignInPage /></LangProvider>)
    await waitFor(() => expect(document.documentElement.dir).toBe('rtl'))
    const user = userEvent.setup()
    const inputs = document.querySelectorAll('input')
    await user.type(inputs[0] as HTMLInputElement, 'o@x.test')
    await user.type(inputs[1] as HTMLInputElement, 'pw')
    await user.click(screen.getByRole('button', { name: /دخول|تسجيل/ }))
    await waitFor(() => expect(localStorage.getItem('vc_lang')).toBe('en'))
    expect(document.documentElement.dir).toBe('ltr')
  })
})
