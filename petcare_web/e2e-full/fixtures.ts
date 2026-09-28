/**
 * Journey fixtures (D0). Test titles carry their journey and screen ids — `[J-00]`, `@S:PUB-01` — which
 * e2e-full/report.mjs turns into e2e/JOURNEYS.md and product/SCREENS.md.
 */
import { test as base, expect, Page } from '@playwright/test'

export type Lang = 'ar' | 'en'
export const SEED_PASSWORD = 'E2E-only-Passw0rd!'
export const USERS = {
  owner: 'owner@e2e.test',
  vet: 'vet@e2e.test',
  clinicAdmin: 'clinic-admin@e2e.test',
  platformAdmin: 'platform-admin@e2e.test',
} as const

export const test = base.extend<{ lang: Lang }>({
  lang: ['ar', { option: true }],
  page: async ({ page, lang }, use) => {
    // Arabic projects store NO preference: they exercise the new-visitor default. English stores the choice.
    if (lang === 'en') await page.addInitScript(() => { try { localStorage.setItem('vc_lang', 'en') } catch { /* */ } })
    await use(page)
  },
})
export { expect }

/** Sign in through the real sign-in screen (web -> API -> PostgreSQL). */
export async function signIn(page: Page, email: string, password = SEED_PASSWORD) {
  await page.goto('/signin')
  // `next dev` compiles on first visit; wait until the client has hydrated so the submit reaches React's handler.
  await page.waitForLoadState('networkidle')
  await page.locator('input[type="email"]').fill(email)
  await page.locator('input[type="password"]').fill(password)
  await page.locator('form button[type="submit"]').click()
}

/** The FAKE email adapter's outbox: the newest message of `template` sent to `to`, as a same-origin path+query. */
export async function lastEmailLink(to: string, template: 'EMAIL_VERIFICATION' | 'PASSWORD_RESET'): Promise<string> {
  const fs = await import('node:fs')
  const file = process.env.PETCARE_E2E_OUTBOX as string
  for (let i = 0; i < 40; i++) {
    const lines = fs.existsSync(file) ? fs.readFileSync(file, 'utf8').split('\n').filter(Boolean) : []
    const hit = lines.map(l => JSON.parse(l)).reverse().find(m => m.to === to && m.template === template)
    if (hit) { expect(hit.label).toBe('FAKE'); const u = new URL(hit.params.link); return u.pathname + u.search }
    await new Promise(r => setTimeout(r, 250))
  }
  throw new Error(`no ${template} email for ${to}`)
}

/** X1: in Arabic, visible text carries no Latin word other than brand/technical tokens. */
export const LATIN_ALLOWED = new Set(['VetiCare', 'MyVetiCare', 'EN', 'AR', 'PDPL', 'SA'])
export async function untranslated(page: Page, selector = 'body'): Promise<string[]> {
  const text = await page.locator(selector).innerText()
  return [...new Set((text.match(/[A-Za-z][A-Za-z'’-]*/g) ?? []).filter(w => !LATIN_ALLOWED.has(w)))]
}

/** A real user closes the owner's first-run guide before using the page (it is dismissable with Esc by design). */
export async function dismissFirstRun(page: Page) {
  const guide = page.locator('[role="dialog"][aria-labelledby="firstrun-title"]')
  if (await guide.isVisible().catch(() => false)) {
    await page.keyboard.press('Escape')
    await expect(guide).toBeHidden()
  }
}
