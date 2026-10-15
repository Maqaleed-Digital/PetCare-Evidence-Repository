# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: jo8-cod.spec.ts >> [J-O8-COD] an owner orders a GENERAL product with cash on delivery and reads the receipt once a licensed pharmacy delivers
- Location: e2e-full/jo8-cod.spec.ts:30:5

# Error details

```
Test timeout of 90000ms exceeded.
```

```
Error: expect(page).toHaveURL(expected) failed

Expected pattern: /\/owner/
Received string:  "http://localhost:3100/signin"

Call log:
  - Expect "toHaveURL" with timeout 30000ms
    11 × unexpected value "http://localhost:3100/signin"

```

```yaml
- navigation:
  - link "VetiCare":
    - /url: /
  - link "الرئيسية":
    - /url: /
  - link "العيادات":
    - /url: /onboarding
  - button "Switch to English": EN / AR
  - text: مالكة تجريبيةمالك
  - link "حسابي":
    - /url: /account
  - button "تسجيل الخروج"
- main:
  - text: VetiCare تسجيل الدخول إلى حسابك
  - paragraph: أدخل بياناتك للوصول إلى منصة VetiCare
  - text: البريد الإلكتروني
  - textbox "البريد الإلكتروني": owner.jo8.ar-desktop.1792079930208@e2e.test
  - text: كلمة المرور
  - textbox "كلمة المرور": Owner-passw0rd-1
  - button "تسجيل الدخول"
  - link "نسيت كلمة المرور؟":
    - /url: /forgot-password
  - paragraph: الوصول بدعوة فقط. إذا كان لديك رمز دعوة من فريق التجريب، سجّل حسابك.
  - paragraph:
    - link "لديك رمز دعوة؟ سجّل الآن":
      - /url: /register
  - paragraph:
    - link "→ العودة للرئيسية":
      - /url: /
- contentinfo:
  - text: منصة مقاليد بيطري بدعم من VetiCare مرحلة التجريب — الإقامة قيد التأكيد، تقييم أثر حماية البيانات قيد التنفيذ
  - link "سياسة الخصوصية":
    - /url: /privacy
  - link "حقوقك تحت نظام حماية البيانات (PDPL)":
    - /url: /account
- alert
```

# Test source

```ts
  8   | export const SEED_PASSWORD = 'E2E-only-Passw0rd!'
  9   | export const USERS = {
  10  |   owner: 'owner@e2e.test',
  11  |   vet: 'vet@e2e.test',
  12  |   clinicAdmin: 'clinic-admin@e2e.test',
  13  |   platformAdmin: 'platform-admin@e2e.test',
  14  | } as const
  15  | 
  16  | export const test = base.extend<{ lang: Lang }>({
  17  |   lang: ['ar', { option: true }],
  18  |   page: async ({ page, lang }, use) => {
  19  |     // Arabic projects store NO preference: they exercise the new-visitor default. English stores the choice.
  20  |     if (lang === 'en') await page.addInitScript(() => { try { localStorage.setItem('vc_lang', 'en') } catch { /* */ } })
  21  |     await use(page)
  22  |   },
  23  | })
  24  | export { expect }
  25  | 
  26  | /** Sign in through the real sign-in screen (web -> API -> PostgreSQL). */
  27  | export async function signIn(page: Page, email: string, password = SEED_PASSWORD) {
  28  |   await page.goto('/signin')
  29  |   // `next dev` compiles on first visit; wait until the client has hydrated so the submit reaches React's handler.
  30  |   await page.waitForLoadState('networkidle')
  31  |   await page.locator('input[type="email"]').fill(email)
  32  |   await page.locator('input[type="password"]').fill(password)
  33  |   await page.locator('form button[type="submit"]').click()
  34  | }
  35  | 
  36  | /** The FAKE email adapter's outbox: the newest message of `template` sent to `to`, as a same-origin path+query. */
  37  | export async function lastEmailLink(to: string, template: 'EMAIL_VERIFICATION' | 'PASSWORD_RESET'): Promise<string> {
  38  |   const fs = await import('node:fs')
  39  |   const file = process.env.PETCARE_E2E_OUTBOX as string
  40  |   for (let i = 0; i < 40; i++) {
  41  |     const lines = fs.existsSync(file) ? fs.readFileSync(file, 'utf8').split('\n').filter(Boolean) : []
  42  |     const hit = lines.map(l => JSON.parse(l)).reverse().find(m => m.to === to && m.template === template)
  43  |     if (hit) { expect(hit.label).toBe('FAKE'); const u = new URL(hit.params.link); return u.pathname + u.search }
  44  |     await new Promise(r => setTimeout(r, 250))
  45  |   }
  46  |   throw new Error(`no ${template} email for ${to}`)
  47  | }
  48  | 
  49  | /** X1: in Arabic, visible text carries no Latin word other than brand/technical tokens. */
  50  | export const LATIN_ALLOWED = new Set(['VetiCare', 'MyVetiCare', 'EN', 'AR', 'PDPL', 'SA'])
  51  | /** The registered product name is one brand token, not three English words. */
  52  | export const BRAND_PHRASES = ['Maqaleed Vet by VetiCare']
  53  | export async function untranslated(page: Page, selector = 'body'): Promise<string[]> {
  54  |   // Machine values the reader must copy verbatim (an MFA key, a recovery code) are marked translate="no" or set in <code>.
  55  |   const text = await page.locator(selector).evaluate((root: HTMLElement) => {
  56  |     const copy = root.cloneNode(true) as HTMLElement
  57  |     copy.querySelectorAll('code, [translate="no"], script, style').forEach(n => n.remove())
  58  |     document.body.appendChild(copy)
  59  |     const t = copy.innerText
  60  |     copy.remove()
  61  |     return t
  62  |   })
  63  |   const scanned = BRAND_PHRASES.reduce((t, b) => t.split(b).join(' '), text)
  64  |   return [...new Set((scanned.match(/[A-Za-z][A-Za-z'’-]*/g) ?? []).filter(w => !LATIN_ALLOWED.has(w)))]
  65  | }
  66  | 
  67  | /** A real user closes the owner's first-run guide before using the page (it is dismissable with Esc by design). */
  68  | export async function dismissFirstRun(page: Page) {
  69  |   const guide = page.locator('[role="dialog"][aria-labelledby="firstrun-title"]')
  70  |   // The guide opens in an effect after hydration, which can lag under a loaded full-suite run (D2e finding
  71  |   // D2E-FIRSTRUN-RACE): wait briefly for it instead of sampling visibility once.
  72  |   if (await guide.waitFor({ state: 'visible', timeout: 5_000 }).then(() => true, () => false)) {
  73  |     await page.keyboard.press('Escape')
  74  |     await expect(guide).toBeHidden()
  75  |   }
  76  | }
  77  | 
  78  | /** RFC 6238 TOTP (SHA-1, 6 digits, 30 s) from a Base32 secret — the journey plays the owner's authenticator app. */
  79  | export async function totp(secretB32: string, at = Date.now()): Promise<string> {
  80  |   const crypto = await import('node:crypto')
  81  |   const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
  82  |   let bits = ''
  83  |   for (const ch of secretB32.replace(/=+$/, '').toUpperCase()) bits += alphabet.indexOf(ch).toString(2).padStart(5, '0')
  84  |   const key = Buffer.from((bits.match(/.{8}/g) ?? []).map(b => parseInt(b, 2)))
  85  |   const counter = Buffer.alloc(8)
  86  |   counter.writeBigUInt64BE(BigInt(Math.floor(at / 1000 / 30)))
  87  |   const mac = crypto.createHmac('sha1', key).update(counter).digest()
  88  |   const off = mac[mac.length - 1] & 0x0f
  89  |   return String((mac.readUInt32BE(off) & 0x7fffffff) % 1_000_000).padStart(6, '0')
  90  | }
  91  | 
  92  | /** A new, email-verified owner signed in on /owner — each journey owns its account, so projects never collide. */
  93  | export async function newOwner(page: Page, info: { project: { name: string } }, tag: string, lang: Lang = 'en'): Promise<{ email: string; password: string }> {
  94  |   const email = `owner.${tag}.${info.project.name}.${Date.now()}@e2e.test`
  95  |   const password = 'Owner-passw0rd-1'
  96  |   await page.goto('/signup')
  97  |   await page.waitForLoadState('networkidle')
  98  |   const form = page.getByTestId('self-register-form')
  99  |   await form.locator('input[autocomplete="name"]').fill(lang === 'ar' ? 'مالكة تجريبية' : 'Test Owner')
  100 |   await form.locator('input[type="email"]').fill(email)
  101 |   await form.locator('input[type="password"]').fill(password)
  102 |   await form.getByTestId('self-register-privacy').check()          // care reminders stay unticked (D2d R13.3)
  103 |   await form.locator('button[type="submit"]').click()
  104 |   await expect(page.getByTestId('self-register-sent')).toBeVisible()
  105 |   await page.goto(await lastEmailLink(email, 'EMAIL_VERIFICATION'))
  106 |   await expect(page.getByTestId('verify-ok')).toBeVisible()
  107 |   await signIn(page, email, password)
> 108 |   await expect(page).toHaveURL(/\/owner/)
      |                      ^ Error: expect(page).toHaveURL(expected) failed
  109 |   await page.waitForLoadState('networkidle')
  110 |   await dismissFirstRun(page)
  111 |   return { email, password }
  112 | }
  113 | 
```