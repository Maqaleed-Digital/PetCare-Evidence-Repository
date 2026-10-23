/**
 * J-V3 — a veterinarian works a consultation in the workspace (MVC-EPC-D-001 D3c, R21.4; CV-05).
 * Full stack: browser -> petcare_web -> main:app -> PostgreSQL; nothing is mocked and no provider is involved. The seeded owner
 * adds a pet and the seeded veterinarian starts an in-person consultation through their own API sessions (no screen starts a
 * consultation from a booking yet — finding D3C-BOOKING-TO-CONSULTATION-NO-SCREEN); everything after that is the console:
 * queue -> workspace -> SOAP draft with a template -> saved and read back -> outcome -> the visit leaves the queue.
 * The draft stays UNSIGNED (signing is J-V4). The CI run serves all four projects from one stack; each project uses its own
 * consultation and completes it, so no open consultation is left behind.
 */
import { request as pwRequest, APIRequestContext } from '@playwright/test'
import { test, expect, signIn, untranslated, USERS, SEED_PASSWORD } from './fixtures'

const API = process.env.PETCARE_E2E_API ?? 'http://localhost:8090'
const OWNER_NAME = 'مالك تجريبي'          // the seeded owner's full name (tools/e2e_stack.py USERS)

async function session(email: string): Promise<APIRequestContext> {
  const probe = await pwRequest.newContext({ baseURL: API })
  const r = await probe.post('/api/auth/sign-in', { data: { email, password: SEED_PASSWORD } })
  expect(r.status(), await r.text()).toBe(200)
  const cookie = r.headersArray().filter(h => h.name.toLowerCase() === 'set-cookie')
    .map(h => h.value.split(';')[0]).find(v => v.startsWith('petcare_session='))
  await probe.dispose()
  return pwRequest.newContext({ baseURL: API, extraHTTPHeaders: { cookie: cookie as string } })
}

test('[J-V3] @S:CV-05 a veterinarian works a consultation in the workspace: SOAP draft from a template, saved, then the outcome', async ({ page, lang }) => {
  const ar = lang === 'ar'
  const petName = ar ? 'ميشا' : 'Misha'
  const owner = await session(USERS.owner)
  const pet = await owner.post('/api/pets', { data: { name: petName, species: ar ? 'قطة' : 'cat' } })
  expect(pet.status(), await pet.text()).toBe(200)
  const petId = (await pet.json()).pet_id as string
  const ownerId = (await (await owner.get('/api/auth/me')).json()).user_id as string
  const vetApi = await session(USERS.vet)
  const started = await vetApi.post('/api/consultations', { data: { pet_id: petId, owner_id: ownerId, veterinarian_id: 'u-e2e-vet' } })
  expect(started.status(), await started.text()).toBe(200)
  const sid = (await started.json()).session_id as string
  await vetApi.dispose()

  // CV-03 -> CV-05: the open consultation is in the veterinarian's queue and opens its workspace
  await signIn(page, USERS.vet)
  await expect(page).toHaveURL(/\/vet/)
  await page.goto('/vet')
  await page.getByTestId('vet-open-queue').click()
  await expect(page).toHaveURL(/\/vet\/queue$/)
  const row = page.locator(`[data-testid="queue-open-consultation"][data-session="${sid}"]`)
  await expect(row).toBeVisible()
  await row.getByTestId('queue-open-workspace').click()
  await expect(page).toHaveURL(new RegExp(`/vet/consultations/${sid}$`))
  await expect(page.getByTestId('workspace-header')).toHaveAttribute('data-status', 'REQUESTED')
  await expect(page.getByTestId('workspace-pet')).toContainText(petName)
  await expect(page.getByTestId('workspace-owner')).toHaveText(OWNER_NAME)
  await expect(page.getByTestId('soap-draft-status')).toHaveAttribute('data-status', 'NONE')

  // A template fills only the empty sections: what the veterinarian already wrote stays
  const subjective = ar ? 'يعرج على الساق الخلفية منذ يومين.' : 'Limping on the hind leg for two days.'
  await page.getByTestId('soap-subjective').fill(subjective)
  await page.getByTestId('soap-template').selectOption('SOAP_GENERAL')
  await page.getByTestId('soap-apply-template').click()
  await expect(page.getByTestId('soap-subjective')).toHaveValue(subjective)
  await expect(page.getByTestId('soap-objective')).toHaveValue(ar ? /^الوزن \(كغ\):/ : /^Weight \(kg\):/)
  const assessment = ar ? 'التواء بسيط في الأنسجة الرخوة.' : 'Mild soft-tissue sprain.'
  await page.getByTestId('soap-assessment').fill(assessment)
  if (ar) {
    await expect(page.locator('main')).toHaveAttribute('dir', 'rtl')
    expect(await untranslated(page, 'main')).toEqual([])
  }
  await page.getByTestId('soap-save').click()
  await expect(page.getByTestId('soap-saved')).toBeVisible()
  await expect(page.getByTestId('soap-draft-status')).toHaveAttribute('data-status', 'DRAFT')
  await expect(page.getByTestId('soap-draft-status')).toHaveAttribute('data-versions', '1')

  // A second version; the server holds the latest, unsigned, and the page reads it back after a reload
  const plan = ar ? 'راحة سبعة أيام، ومتابعة بعد أسبوعين.' : 'Rest for seven days; follow-up in two weeks.'
  await page.getByTestId('soap-plan').fill(plan)
  await page.getByTestId('soap-save').click()
  await expect(page.getByTestId('soap-draft-status')).toHaveAttribute('data-versions', '2')
  await page.reload()
  await expect(page.getByTestId('soap-subjective')).toHaveValue(subjective)
  await expect(page.getByTestId('soap-assessment')).toHaveValue(assessment)
  await expect(page.getByTestId('soap-plan')).toHaveValue(plan)
  await expect(page.getByTestId('soap-template')).toHaveValue('SOAP_GENERAL')
  await expect(page.getByTestId('soap-draft-status')).toHaveAttribute('data-status', 'DRAFT')
  await expect(page.locator('[data-testid*="sign"]')).toHaveCount(0)                  // signing is J-V4, not offered here

  // The owner has no workspace; the outcome completes the visit and it leaves the queue
  expect((await owner.get(`/api/vet/consultations/${sid}/workspace`)).status()).toBe(403)
  await owner.dispose()
  const outcome = ar ? 'التواء بسيط؛ راحة.' : 'Mild sprain; rest.'
  await page.getByTestId('outcome-text').fill(outcome)
  await page.getByTestId('outcome-record').click()
  await expect(page.getByTestId('workspace-header')).toHaveAttribute('data-status', 'COMPLETED')
  await expect(page.getByTestId('workspace-outcome')).toHaveText(outcome)
  await expect(page.getByTestId('soap-plan')).toHaveValue(plan)                         // the draft is kept with the visit
  if (ar) expect(await untranslated(page, 'main')).toEqual([])
  await page.getByTestId('workspace-back').click()
  await expect(page).toHaveURL(/\/vet\/queue$/)
  await expect(page.getByTestId('vet-queue')).toBeVisible()
  await expect(page.locator(`[data-testid="queue-open-consultation"][data-session="${sid}"]`)).toHaveCount(0)
})
