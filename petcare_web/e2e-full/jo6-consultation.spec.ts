/**
 * J-O6 (chat and files part) — an owner attends their consultation: secure messages and a shared file with the
 * veterinarian (CO-09), entered from the owner home. Full stack: browser -> petcare_web -> main:app -> PostgreSQL; no
 * MyVetiCare API is mocked. The veterinarian (whose console is D3) starts the consultation and replies through their
 * own API session. X-27 end to end: the served app starts the consultation only for the owner's own pet.
 *
 * NOT CLAIMED HERE: the video part of J-O6. Remote consultation is closed until the KSA telemedicine counsel
 * determination is recorded (AC-FR-06-05, COUNSEL:REG-02), so the CO-08 waiting room is proven only in its served
 * fail-closed state, and this test is tagged J-O6-CHAT, not J-O6 — the journey matrix must not count J-O6 or CO-08 as
 * PASS on chat alone (D2f finding D2F-JO6-VIDEO-GATED).
 */
import { request as pwRequest, APIRequestContext } from '@playwright/test'
import { test, expect, newOwner, dismissFirstRun, untranslated, USERS, SEED_PASSWORD } from './fixtures'

const API = process.env.PETCARE_E2E_API ?? 'http://localhost:8090'
const PNG = Buffer.from('89504e470d0a1a0a0000000d4948445200000001000000010806000000' +
  '1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082', 'hex')

async function staff(email: string): Promise<APIRequestContext> {
  const probe = await pwRequest.newContext({ baseURL: API })
  const r = await probe.post('/api/auth/sign-in', { data: { email, password: SEED_PASSWORD } })
  expect(r.status(), await r.text()).toBe(200)
  const cookie = r.headersArray().filter(h => h.name.toLowerCase() === 'set-cookie')
    .map(h => h.value.split(';')[0]).find(v => v.startsWith('petcare_session='))
  expect(cookie).toBeTruthy()
  await probe.dispose()
  return pwRequest.newContext({ baseURL: API, extraHTTPHeaders: { cookie: cookie as string } })
}

test('[J-O6-CHAT] @S:CO-09 an owner exchanges messages and a file with the veterinarian in their own consultation', async ({ page, lang }, info) => {
  await newOwner(page, info, 'jo6', lang)
  const me = await (await page.request.get(`${API}/api/auth/me`)).json()
  const petName = lang === 'ar' ? 'لونا' : 'Luna'
  const pet = await page.request.post(`${API}/api/pets`, { data: { name: petName, species: 'cat' } })
  expect(pet.status()).toBe(200)
  const petId = (await pet.json()).pet_id as string

  // X-27 on the served app: the veterinarian cannot start a consultation for a pet that is not the selected owner's
  const vet = await staff(USERS.vet)
  const foreign = await vet.post('/api/consultations', { data: { pet_id: petId, owner_id: 'u-e2e-owner', veterinarian_id: 'u-e2e-vet' } })
  expect(foreign.status()).toBe(400)
  expect((await foreign.json()).detail.error).toBe('PET_NOT_OF_OWNER')
  const missing = await vet.post('/api/consultations', { data: { pet_id: 'no-such-pet', owner_id: me.user_id, veterinarian_id: 'u-e2e-vet' } })
  expect(missing.status()).toBe(400)
  const started = await vet.post('/api/consultations', { data: { pet_id: petId, owner_id: me.user_id, veterinarian_id: 'u-e2e-vet' } })
  expect(started.status(), await started.text()).toBe(200)
  const cid = (await started.json()).session_id as string

  // Reached from the owner home, not typed in
  await page.goto('/owner')
  await page.waitForLoadState('networkidle')
  await dismissFirstRun(page)
  await page.getByTestId('owner-open-consultations').click()
  await expect(page).toHaveURL(/\/owner\/consultations$/)
  const row = page.getByTestId('owner-consultation')
  await expect(row).toHaveCount(1)
  await expect(row.getByText(petName)).toBeVisible()
  if (lang === 'ar') expect(await untranslated(page, 'main')).toEqual([])
  await row.getByTestId('consultation-open-messages').click()
  await expect(page).toHaveURL(new RegExp(`/owner/consultations/messages\\?consultation=${cid}$`))
  await page.waitForLoadState('networkidle')

  // The owner writes and shares a photo; the server holds both
  const text = lang === 'ar' ? 'لونا تسعل منذ يومين' : 'Luna has been coughing for two days'
  await page.locator('textarea[name="body"]').fill(text)
  await page.getByTestId('message-file').setInputFiles({ name: 'luna.png', mimeType: 'image/png', buffer: PNG })
  await page.getByTestId('message-send').click()
  const mine = page.getByTestId('message').filter({ hasText: text })
  await expect(mine).toHaveAttribute('data-sender-role', 'owner')
  await expect(mine.getByTestId('message-attachment')).toContainText('luna.png')
  await expect(page.getByTestId('message-problem')).toHaveCount(0)
  const held = await (await vet.get(`/api/consultations/${cid}/messages`)).json()
  expect(held.map((m: { body: string }) => m.body)).toEqual([text])
  expect(held[0].attachments.map((a: { filename: string }) => a.filename)).toEqual(['luna.png'])

  // The veterinarian replies; the owner sees it after reloading the served thread, and can download the shared file
  const reply = lang === 'ar' ? 'شكراً، يرجى قياس الحرارة' : 'Thank you, please take her temperature'
  expect((await vet.post(`/api/consultations/${cid}/messages`, { data: { body: reply } })).status()).toBe(200)
  await page.reload()
  await page.waitForLoadState('networkidle')
  await expect(page.getByTestId('message').filter({ hasText: reply })).toHaveAttribute('data-sender-role', 'veterinarian')
  const href = await mine.getByTestId('message-attachment').getAttribute('href')
  const file = await page.request.get(href as string)
  expect(file.status()).toBe(200)
  expect(Buffer.from(await file.body()).equals(PNG)).toBe(true)
  if (lang === 'ar') expect(await untranslated(page, 'main')).toEqual([])

  // CO-08 waiting room, served state: remote consultation is closed until counsel, so no device or call control at all
  await page.goto(`/owner/consultations/video?consultation=${cid}`)
  await expect(page.getByTestId('video-room-closed')).toHaveAttribute('data-reason', 'counsel')
  await expect(page.getByTestId('video-room-check')).toHaveCount(0)
  await expect(page.getByTestId('video-room-join')).toHaveCount(0)
  await vet.dispose()
})
