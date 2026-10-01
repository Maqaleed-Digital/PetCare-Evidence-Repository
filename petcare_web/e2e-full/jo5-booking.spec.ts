/**
 * J-O5 — an owner books a consultation with a veterinarian of their clinic, views it, reschedules it and cancels it
 * (CO-05 book, CO-07 my appointments). Full stack: browser → petcare_web → main:app → PostgreSQL. The four projects
 * book the same seeded veterinarian concurrently, so a slot can be taken between listing and booking: the journey then
 * sees the served SLOT_TAKEN refusal and picks another slot — which is itself the double-booking rule, end to end.
 */
import { Page } from '@playwright/test'
import { test, expect, newOwner, untranslated, dismissFirstRun } from './fixtures'

async function addPet(page: Page, name: string, species: string) {
  await page.goto('/owner/pets')
  await page.waitForLoadState('networkidle')
  const form = page.locator('form').filter({ has: page.locator('input[name="species"]') })
  await form.locator('input[name="name"]').fill(name)
  await form.locator('input[name="species"]').fill(species)
  await form.locator('button[type="submit"]').click()
  await expect(page.getByRole('button', { name: `${name} · ${species}` })).toBeVisible()
}

/** Pick a free served slot (not `avoid`) and submit; on a served SLOT_TAKEN pick again. Returns the booked slot. */
async function pickAndSubmit(page: Page, avoid?: string): Promise<string> {
  for (let attempt = 0; attempt < 5; attempt++) {
    const radios = page.getByTestId('book-slots').locator('input[type="radio"]')
    await expect(radios.first()).toBeVisible()
    const values = (await radios.evaluateAll(els => els.map(e => (e as HTMLInputElement).value))).filter(v => v !== avoid)
    const value = values[Math.floor(Math.random() * Math.min(values.length, 16))]
    await page.getByTestId('book-slots').locator(`input[value="${value}"]`).check()
    await page.getByTestId('book-submit').click()
    const done = await Promise.race([
      page.waitForURL('**/owner/appointments', { timeout: 30_000, waitUntil: 'domcontentloaded' }).then(() => true),
      page.getByTestId('book-problem').waitFor({ timeout: 30_000 }).then(() => false),
    ])
    if (done) return value
  }
  throw new Error('no slot could be booked')
}

test('[J-O5] @S:CO-05 @S:CO-07 an owner books, views, reschedules and cancels a consultation', async ({ page, lang }, info) => {
  await newOwner(page, info, 'jo5', lang)
  const name = lang === 'ar' ? 'بسكويت' : 'Biscuit'
  const species = lang === 'ar' ? 'كلب' : 'dog'
  await addPet(page, name, species)

  // Reached from the owner home, not typed in
  await page.goto('/owner')
  await page.waitForLoadState('networkidle')
  await dismissFirstRun(page)
  await page.getByTestId('owner-open-book').click()
  await expect(page).toHaveURL(/\/owner\/book$/)
  await page.waitForLoadState('networkidle')
  const form = page.getByTestId('book-form')
  await expect(form.locator('select[name="pet"] option')).toHaveText([`${name} · ${species}`])
  await expect(form.locator('select[name="vet"] option')).toHaveText(['طبيب تجريبي'])   // the seeded clinic veterinarian
  await form.locator('textarea[name="reason"]').fill(lang === 'ar' ? 'فحص سنوي' : 'Annual check')
  if (lang === 'ar') expect(await untranslated(page, 'main')).toEqual([])
  const first = await pickAndSubmit(page)

  // CO-07: the server's booking, in the owner's list
  const row = page.getByTestId('appointment')
  await expect(row).toHaveCount(1)
  await expect(row).toHaveAttribute('data-status', 'BOOKED')
  await expect(row.getByText(name)).toBeVisible()
  await expect(row.locator('time')).toHaveAttribute('datetime', first)
  if (lang === 'ar') expect(await untranslated(page, 'main')).toEqual([])

  // Reschedule to another served slot
  await row.getByTestId('appointment-reschedule').click()
  await expect(page).toHaveURL(/\/owner\/book\?reschedule=/)
  await page.waitForLoadState('networkidle')
  const second = await pickAndSubmit(page, first)
  await expect(page.getByTestId('appointment')).toHaveCount(1)
  await expect(page.getByTestId('appointment').locator('time')).toHaveAttribute('datetime', second)

  // Cancel: one click asks, the confirmation cancels; the server keeps the cancelled record
  await page.getByTestId('appointment-cancel').click()
  await page.getByTestId('appointment-cancel-confirm').click()
  await expect(page.getByTestId('appointment')).toHaveAttribute('data-status', 'CANCELLED')
  await page.reload()
  await page.waitForLoadState('networkidle')
  await expect(page.getByTestId('appointment')).toHaveAttribute('data-status', 'CANCELLED')
  await expect(page.getByTestId('appointment-cancel')).toHaveCount(0)
})
