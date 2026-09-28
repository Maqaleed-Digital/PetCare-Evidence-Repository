'use client'

/**
 * Account flows for owner self-registration (MVC-EPC-D-001 Lane D, D2 — J-O1). Server-driven: the API decides whether
 * self-registration is enabled (Sponsor ruling 1: production default OFF), verifies email through its governed adapter,
 * and issues/consumes one-time tokens. Passwords live only in component state and are cleared once sent.
 */

import { FormEvent, useEffect, useState } from 'react'
import { Button, Copy, Field, Notice, useCopy } from '@/components/ui'

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
const post = (path: string, body: unknown) => fetch(`${apiBase}${path}`, {
  method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
})

export const AC = {
  selfTitle: { ar: 'إنشاء حساب مالك', en: 'Create an owner account' },
  name: { ar: 'الاسم الكامل', en: 'Full name' },
  email: { ar: 'البريد الإلكتروني', en: 'Email' },
  password: { ar: 'كلمة المرور', en: 'Password' },
  passwordHint: { ar: 'عشرة أحرف على الأقل.', en: 'At least ten characters.' },
  consent: { ar: 'أوافق على إشعار الخصوصية وفق نظام حماية البيانات الشخصية.', en: 'I agree to the privacy notice under the Saudi PDPL.' },
  create: { ar: 'إنشاء الحساب', en: 'Create account' },
  checkEmail: { ar: 'أرسلنا رابط تأكيد إلى بريدك الإلكتروني. افتحه لتفعيل حسابك ثم سجّل الدخول.', en: 'We sent a confirmation link to your email. Open it to activate your account, then sign in.' },
  exists: { ar: 'هذا البريد مسجّل بالفعل.', en: 'This email is already registered.' },
  tooShort: { ar: 'كلمة المرور قصيرة جداً.', en: 'The password is too short.' },
  unavailable: { ar: 'التسجيل غير متاح حالياً. حاول لاحقاً.', en: 'Registration is not available right now. Try again later.' },
  invalid: { ar: 'تحقق من البيانات المدخلة.', en: 'Check the details you entered.' },
  verifyTitle: { ar: 'تأكيد البريد الإلكتروني', en: 'Confirm your email' },
  verifying: { ar: 'جارٍ التأكيد…', en: 'Confirming…' },
  verified: { ar: 'تم تأكيد بريدك الإلكتروني. يمكنك الآن تسجيل الدخول.', en: 'Your email is confirmed. You can now sign in.' },
  linkInvalid: { ar: 'الرابط غير صالح أو منتهي الصلاحية.', en: 'This link is invalid or has expired.' },
  signIn: { ar: 'تسجيل الدخول', en: 'Sign in' },
  forgotTitle: { ar: 'نسيت كلمة المرور', en: 'Forgot your password' },
  forgotIntro: { ar: 'أدخل بريدك الإلكتروني وسنرسل رابطاً لإعادة تعيين كلمة المرور إن كان الحساب موجوداً.', en: 'Enter your email and we will send a reset link if the account exists.' },
  send: { ar: 'إرسال الرابط', en: 'Send link' },
  forgotSent: { ar: 'إن كان البريد مسجّلاً فستصلك رسالة خلال دقائق.', en: 'If that email is registered, a message is on its way.' },
  resetTitle: { ar: 'تعيين كلمة مرور جديدة', en: 'Set a new password' },
  newPassword: { ar: 'كلمة المرور الجديدة', en: 'New password' },
  save: { ar: 'حفظ', en: 'Save' },
  resetDone: { ar: 'تم تغيير كلمة المرور وإنهاء جميع الجلسات. سجّل الدخول بكلمة المرور الجديدة.', en: 'Your password was changed and every session was ended. Sign in with the new password.' },
} satisfies Record<string, Copy>

export function useSelfRegistrationEnabled(): boolean | null {
  const [enabled, setEnabled] = useState<boolean | null>(null)
  useEffect(() => {
    let live = true
    fetch(`${apiBase}/api/auth/registration-options`, { credentials: 'include' })
      .then(r => (r.ok ? r.json() : null))
      .then(b => { if (live) setEnabled(b?.owner_self_registration === true) })
      .catch(() => { if (live) setEnabled(false) })
    return () => { live = false }
  }, [])
  return enabled
}

export function SelfRegisterForm() {
  const { lang, tr } = useCopy()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [consent, setConsent] = useState(false)
  const [state, setState] = useState<'idle' | 'busy' | 'sent'>('idle')
  const [error, setError] = useState('')

  async function submit(e: FormEvent) {
    e.preventDefault()
    const pw = password
    setPassword('')
    setState('busy'); setError('')
    try {
      const r = await post('/api/auth/self-register', { name, email, password: pw, locale: lang })
      if (r.status === 201) { setState('sent'); return }
      const err = (await r.json().catch(() => ({})))?.detail?.error
      setError(tr(err === 'EMAIL_EXISTS' ? AC.exists : err === 'PASSWORD_TOO_SHORT' ? AC.tooShort
        : r.status >= 500 || r.status === 404 ? AC.unavailable : AC.invalid))
    } catch { setError(tr(AC.unavailable)) }
    setState('idle')
  }

  if (state === 'sent') return <Notice tone="success" testId="self-register-sent">{tr(AC.checkEmail)}</Notice>
  return (
    <form onSubmit={submit} className="ds-card" data-testid="self-register-form" aria-labelledby="self-register-title">
      <h2 id="self-register-title" className="title-md">{tr(AC.selfTitle)}</h2>
      <Field label={AC.name} value={name} onChange={e => setName(e.currentTarget.value)} required autoComplete="name" />
      <Field label={AC.email} type="email" value={email} onChange={e => setEmail(e.currentTarget.value)} required autoComplete="email" />
      <Field label={AC.password} hint={AC.passwordHint} type="password" value={password} minLength={10}
             onChange={e => setPassword(e.currentTarget.value)} required autoComplete="new-password" />
      <label className="ds-row"><input type="checkbox" checked={consent} onChange={e => setConsent(e.currentTarget.checked)} required />
        <span>{tr(AC.consent)} <a className="ds-link" href="/privacy">PDPL</a></span></label>
      {error && <Notice tone="danger" testId="self-register-error">{error}</Notice>}
      <Button type="submit" disabled={state === 'busy' || !consent}>{tr(AC.create)}</Button>
    </form>
  )
}
