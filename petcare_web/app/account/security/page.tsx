'use client'

/**
 * /account/security — two-step verification enrolment (MVC-EPC-B-001 Lane B, B4/B5).
 *
 * The SERVER chooses the path (petcare_api/main.py `mfa_enrol`): with no active factor it answers 401
 * PRIMARY_REAUTHENTICATION_REQUIRED and the password is re-entered for THIS operation; with an active factor it answers
 * 403 MFA_STEP_UP_REQUIRED (enrolment is always-fresh) and the step-up prompt asks for the existing factor. The page
 * holds no enrolment state of its own beyond the current screen. The ten recovery codes returned by /confirm are shown
 * ONCE; after the user dismisses them they are dropped from memory and there is no way to show them again.
 */

import { FormEvent, useState } from 'react'
import { useLang } from '@/components/LangProvider'
import { useStepUp } from '@/components/StepUp'

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
const post = (path: string, body: unknown) => fetch(`${apiBase}${path}`, {
  method: 'POST', credentials: 'include', cache: 'no-store',
  headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
})

const L = {
  kicker: { ar: 'الحساب', en: 'Account' },
  title: { ar: 'التحقق بخطوتين', en: 'Two-step verification' },
  intro: {
    ar: 'تتطلب العمليات الحساسة (مثل إصدار الوصفات وصرفها) رمزاً من تطبيق المصادقة على هاتفك.',
    en: 'Sensitive operations (such as prescribing and dispensing) require a code from an authenticator app on your phone.',
  },
  start: { ar: 'إعداد التحقق بخطوتين أو استبدال الجهاز', en: 'Set up two-step verification or replace your device' },
  password: { ar: 'كلمة المرور', en: 'Password' },
  reauth: { ar: 'أدخل كلمة المرور لتأكيد أنك صاحب الحساب.', en: 'Enter your password to confirm it is you.' },
  continue: { ar: 'متابعة', en: 'Continue' },
  wrongPassword: { ar: 'كلمة المرور غير صحيحة.', en: 'The password is not correct.' },
  scan: {
    ar: 'أضف الحساب إلى تطبيق المصادقة باستخدام الرابط أو المفتاح أدناه، ثم أدخل الرمز المكوّن من ستة أرقام.',
    en: 'Add the account to your authenticator app with the link or key below, then enter the six-digit code.',
  },
  key: { ar: 'المفتاح', en: 'Key' },
  code: { ar: 'رمز التحقق', en: 'Verification code' },
  confirm: { ar: 'تأكيد', en: 'Confirm' },
  wrongCode: { ar: 'الرمز غير صحيح. حاول مرة أخرى.', en: 'That code is not correct. Try again.' },
  codesTitle: { ar: 'رموز الاسترداد', en: 'Recovery codes' },
  codesWarn: {
    ar: 'احفظ هذه الرموز العشرة الآن في مكان آمن. لن تُعرض مرة أخرى. يصلح كل رمز لعملية واحدة فقط.',
    en: 'Save these ten codes somewhere safe now. They will not be shown again. Each code works for one operation only.',
  },
  copy: { ar: 'نسخ', en: 'Copy' },
  download: { ar: 'تنزيل', en: 'Download' },
  saved: { ar: 'حفظتها — إخفاء الرموز', en: 'I have saved them — hide the codes' },
  done: { ar: 'تم إعداد التحقق بخطوتين.', en: 'Two-step verification is set up.' },
  unsupported: { ar: 'نوع المصادقة غير مدعوم.', en: 'That verification method is not supported.' },
  failed: { ar: 'تعذر إكمال الإعداد. حاول لاحقاً.', en: 'Setup could not be completed. Try again later.' },
} as const

type Phase = 'start' | 'password' | 'confirm' | 'codes' | 'done'

function secretOf(uri: string): string {
  try { return new URL(uri).searchParams.get('secret') ?? '' } catch { return '' }
}

export default function SecurityPage() {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  const t = (k: keyof typeof L) => L[k][isAr ? 'ar' : 'en']
  const { stepUpFetch, stepUpUi } = useStepUp()
  const [phase, setPhase] = useState<Phase>('start')
  const [uri, setUri] = useState('')
  const [codes, setCodes] = useState<string[]>([])
  const [error, setError] = useState('')
  // Controlled so they are provably emptied the moment they are sent (form.reset() does not clear React inputs).
  const [password, setPassword] = useState('')
  const [code, setCode] = useState('')

  async function enrol(body: Record<string, string>) {
    setError('')
    const { response, state } = await stepUpFetch('/api/me/mfa/enrol', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
    })
    if (state !== 'ok') return
    if (response.ok) {
      setUri((await response.json()).otpauth_uri)
      setPhase('confirm')
      return
    }
    const err = (await response.json().catch(() => ({})))?.detail?.error
    if (err === 'PRIMARY_REAUTHENTICATION_REQUIRED') {
      if (phase === 'password') setError(t('wrongPassword'))
      setPhase('password')
    } else if (err === 'MFA_FACTOR_NOT_SUPPORTED') setError(t('unsupported'))
    else setError(t('failed'))
  }

  async function reauth(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const value = password
    setPassword('')                               // the password does not outlive the request
    await enrol({ password: value })
  }

  async function confirm(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const value = code
    setCode('')
    setError('')
    const r = await post('/api/me/mfa/confirm', { code: value })
    if (r.ok) {
      setUri('')
      setCodes((await r.json()).recovery_codes ?? [])
      setPhase('codes')
    } else setError(r.status === 401 ? t('wrongCode') : t('failed'))
  }

  function download() {
    const url = URL.createObjectURL(new Blob([codes.join('\n') + '\n'], { type: 'text/plain' }))
    const a = document.createElement('a')
    a.href = url
    a.download = 'petcare-recovery-codes.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  function dismissCodes() {
    setCodes([])                                  // gone for good: never stored, never re-displayed
    setPhase('done')
  }

  return (
    <main className="stack" dir={isAr ? 'rtl' : 'ltr'} style={{ maxWidth: 720 }}>
      <div>
        <div className="kicker">{t('kicker')}</div>
        <h1 className="title-lg">{t('title')}</h1>
      </div>
      <p>{t('intro')}</p>

      {phase === 'start' && (
        <button type="button" className="btn" data-testid="mfa-start" onClick={() => void enrol({})}>{t('start')}</button>
      )}

      {phase === 'password' && (
        <form onSubmit={reauth} className="card stack" data-testid="mfa-reauth">
          <p>{t('reauth')}</p>
          <label htmlFor="mfa-password">{t('password')}</label>
          <input id="mfa-password" name="password" type="password" autoComplete="current-password" required
                 value={password} onChange={e => setPassword(e.currentTarget.value)} />
          <button type="submit" className="btn">{t('continue')}</button>
        </form>
      )}

      {phase === 'confirm' && (
        <form onSubmit={confirm} className="card stack" data-testid="mfa-confirm">
          <p>{t('scan')}</p>
          <a href={uri} data-testid="mfa-otpauth">otpauth</a>
          <p>{t('key')}: <code dir="ltr" data-testid="mfa-key">{secretOf(uri)}</code></p>
          <label htmlFor="mfa-code">{t('code')}</label>
          <input id="mfa-code" name="code" inputMode="numeric" autoComplete="one-time-code" required
                 value={code} onChange={e => setCode(e.currentTarget.value)} />
          <button type="submit" className="btn">{t('confirm')}</button>
        </form>
      )}

      {phase === 'codes' && (
        <section className="card stack" data-testid="mfa-codes" aria-labelledby="mfa-codes-title">
          <h2 id="mfa-codes-title" className="title-md">{t('codesTitle')}</h2>
          <p role="note">{t('codesWarn')}</p>
          <ol dir="ltr" data-testid="mfa-code-list">{codes.map(c => <li key={c}><code>{c}</code></li>)}</ol>
          <div className="row">
            <button type="button" className="btn" onClick={() => void navigator.clipboard?.writeText(codes.join('\n'))}>{t('copy')}</button>
            <button type="button" className="btn" onClick={download}>{t('download')}</button>
          </div>
          <button type="button" className="btn" data-testid="mfa-codes-saved" onClick={dismissCodes}>{t('saved')}</button>
        </section>
      )}

      {phase === 'done' && <p role="status" data-testid="mfa-done">{t('done')}</p>}
      {error && <p role="alert" data-testid="mfa-error">{error}</p>}
      {stepUpUi}
    </main>
  )
}
