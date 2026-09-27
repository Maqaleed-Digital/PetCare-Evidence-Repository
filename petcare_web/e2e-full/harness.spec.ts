/**
 * D0 harness proof: the journey suite really runs browser -> web -> API -> PostgreSQL. Not a frozen journey.
 */
import { test, expect, signIn, USERS } from './fixtures'

const API = process.env.PETCARE_E2E_API ?? 'http://localhost:8090'

test('[HARNESS] a seeded owner signs in through the real stack and the server holds the session', async ({ page, lang }) => {
  await signIn(page, USERS.owner)
  await expect(page).toHaveURL(/\/owner/)
  await expect(page.locator('html')).toHaveAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr')
  const me = await page.evaluate(async (api) => {
    const r = await fetch(`${api}/api/auth/me`, { credentials: 'include' })
    return { status: r.status, body: await r.json() }
  }, API)
  expect(me.status).toBe(200)
  expect(me.body.role).toBe('owner')                    // session held in PostgreSQL, read back through main:app
})

test('[HARNESS] a wrong password is refused by the server and no session is created', async ({ page }) => {
  await signIn(page, USERS.owner, 'not-the-password')
  await expect(page).toHaveURL(/\/signin/)
  const status = await page.evaluate(async (api) => (await fetch(`${api}/api/auth/me`, { credentials: 'include' })).status, API)
  expect(status).toBe(401)
})
