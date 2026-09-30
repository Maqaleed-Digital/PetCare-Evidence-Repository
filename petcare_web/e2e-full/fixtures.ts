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
/** The registered product name is one brand token, not three English words. */
export const BRAND_PHRASES = ['Maqaleed Vet by VetiCare']
export async function untranslated(page: Page, selector = 'body'): Promise<string[]> {
  // Machine values the reader must copy verbatim (an MFA key, a recovery code) are marked translate="no" or set in <code>.
  const text = await page.locator(selector).evaluate((root: HTMLElement) => {
    const copy = root.cloneNode(true) as HTMLElement
    copy.querySelectorAll('code, [translate="no"], script, style').forEach(n => n.remove())
    document.body.appendChild(copy)
    const t = copy.innerText
    copy.remove()
    return t
  })
  const scanned = BRAND_PHRASES.reduce((t, b) => t.split(b).join(' '), text)
  return [...new Set((scanned.match(/[A-Za-z][A-Za-z'’-]*/g) ?? []).filter(w => !LATIN_ALLOWED.has(w)))]
}

/** A real user closes the owner's first-run guide before using the page (it is dismissable with Esc by design). */
export async function dismissFirstRun(page: Page) {
  const guide = page.locator('[role="dialog"][aria-labelledby="firstrun-title"]')
  // The guide opens in an effect after hydration, which can lag under a loaded full-suite run (D2e finding
  // D2E-FIRSTRUN-RACE): wait briefly for it instead of sampling visibility once.
  if (await guide.waitFor({ state: 'visible', timeout: 5_000 }).then(() => true, () => false)) {
    await page.keyboard.press('Escape')
    await expect(guide).toBeHidden()
  }
}

/** RFC 6238 TOTP (SHA-1, 6 digits, 30 s) from a Base32 secret — the journey plays the owner's authenticator app. */
export async function totp(secretB32: string, at = Date.now()): Promise<string> {
  const crypto = await import('node:crypto')
  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
  let bits = ''
  for (const ch of secretB32.replace(/=+$/, '').toUpperCase()) bits += alphabet.indexOf(ch).toString(2).padStart(5, '0')
  const key = Buffer.from((bits.match(/.{8}/g) ?? []).map(b => parseInt(b, 2)))
  const counter = Buffer.alloc(8)
  counter.writeBigUInt64BE(BigInt(Math.floor(at / 1000 / 30)))
  const mac = crypto.createHmac('sha1', key).update(counter).digest()
  const off = mac[mac.length - 1] & 0x0f
  return String((mac.readUInt32BE(off) & 0x7fffffff) % 1_000_000).padStart(6, '0')
}

/** A new, email-verified owner signed in on /owner — each journey owns its account, so projects never collide. */
export async function newOwner(page: Page, info: { project: { name: string } }, tag: string, lang: Lang = 'en'): Promise<{ email: string; password: string }> {
  const email = `owner.${tag}.${info.project.name}.${Date.now()}@e2e.test`
  const password = 'Owner-passw0rd-1'
  await page.goto('/signup')
  await page.waitForLoadState('networkidle')
  const form = page.getByTestId('self-register-form')
  await form.locator('input[autocomplete="name"]').fill(lang === 'ar' ? 'مالكة تجريبية' : 'Test Owner')
  await form.locator('input[type="email"]').fill(email)
  await form.locator('input[type="password"]').fill(password)
  await form.getByTestId('self-register-privacy').check()          // care reminders stay unticked (D2d R13.3)
  await form.locator('button[type="submit"]').click()
  await expect(page.getByTestId('self-register-sent')).toBeVisible()
  await page.goto(await lastEmailLink(email, 'EMAIL_VERIFICATION'))
  await expect(page.getByTestId('verify-ok')).toBeVisible()
  await signIn(page, email, password)
  await expect(page).toHaveURL(/\/owner/)
  await page.waitForLoadState('networkidle')
  await dismissFirstRun(page)
  return { email, password }
}
