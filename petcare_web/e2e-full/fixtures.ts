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
