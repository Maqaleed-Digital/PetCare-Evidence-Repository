/**
 * MFA step-up on the web client (MVC-EXTERNAL-PRODUCTION-CLOSURE-001 Lane B, MVC-EPC-B-001).
 *
 * The SERVED APP is the only authority (NFR-08 / Sponsor act MVC-SQ3-NFR08-STEP-UP-001). The client never decides
 * freshness: it keeps no timer, cache or flag that could skip a prompt. It reacts only to the server's machine-readable
 * refusal — HTTP 403 with `detail.error` of `MFA_STEP_UP_REQUIRED` or `MFA_ENROLMENT_REQUIRED`
 * (petcare_api/main.py `_step_up_refusal`) — and retries the ORIGINAL request exactly once after a successful step-up.
 */

export const STEP_UP_REQUIRED = 'MFA_STEP_UP_REQUIRED'
export const ENROLMENT_REQUIRED = 'MFA_ENROLMENT_REQUIRED'

export type StepUpState = 'ok' | 'cancelled' | 'step_up_failed' | 'enrolment_required'
export type StepUpOutcome = { response: Response; state: StepUpState }

/** The server's step-up refusal code carried by `res`, or null. Reads a clone, so the caller can still read the body. */
export async function refusalOf(res: Response): Promise<string | null> {
  if (res.status !== 403) return null
  try {
    const body = await res.clone().json()
    const error = body?.detail?.error
    return error === STEP_UP_REQUIRED || error === ENROLMENT_REQUIRED ? error : null
  } catch {
    return null
  }
}

/**
 * Send; on a step-up refusal ask `prompt` for a step-up; when it succeeds, send the original request ONE more time.
 * A second step-up refusal is returned as `step_up_failed` for the caller to show — never another prompt, never a loop.
 */
export async function withStepUp(send: () => Promise<Response>, prompt: () => Promise<boolean>): Promise<StepUpOutcome> {
  const first = await send()
  const refusal = await refusalOf(first)
  if (refusal === ENROLMENT_REQUIRED) return { response: first, state: 'enrolment_required' }
  if (refusal !== STEP_UP_REQUIRED) return { response: first, state: 'ok' }
  if (!(await prompt())) return { response: first, state: 'cancelled' }
  const second = await send()
  const again = await refusalOf(second)
  if (again === STEP_UP_REQUIRED) return { response: second, state: 'step_up_failed' }
  if (again === ENROLMENT_REQUIRED) return { response: second, state: 'enrolment_required' }
  return { response: second, state: 'ok' }
}

export const SECURITY_PATH = '/account/security'

export const STEP_UP_STRINGS = {
  title: { ar: 'تأكيد الهوية مطلوب', en: 'Verification required' },
  explain: {
    ar: 'هذه عملية حساسة. أدخل الرمز المكوّن من ستة أرقام من تطبيق المصادقة لإكمالها.',
    en: 'This is a sensitive operation. Enter the six-digit code from your authenticator app to continue.',
  },
  code: { ar: 'رمز التحقق', en: 'Verification code' },
  recovery: { ar: 'رمز الاسترداد', en: 'Recovery code' },
  useRecovery: { ar: 'استخدام رمز استرداد بدلاً من ذلك', en: 'Use a recovery code instead' },
  useCode: { ar: 'استخدام رمز التطبيق', en: 'Use an authenticator code' },
  verify: { ar: 'تحقق', en: 'Verify' },
  cancel: { ar: 'إلغاء', en: 'Cancel' },
  invalidCode: { ar: 'الرمز غير صحيح أو مستخدم من قبل. حاول مرة أخرى.', en: 'That code is not valid or was already used. Try again.' },
  invalidRecovery: { ar: 'رمز الاسترداد غير صالح أو مستخدم من قبل.', en: 'That recovery code is not valid or was already used.' },
  unavailable: { ar: 'تعذر التحقق الآن. حاول لاحقاً.', en: 'Verification is unavailable right now. Try again later.' },
  stillRequired: {
    ar: 'لم تكتمل العملية: ما زال الخادم يطلب تأكيد الهوية. لم تُعَد المحاولة تلقائياً.',
    en: 'The operation did not complete: the server still requires verification. It was not retried automatically.',
  },
  enrolmentRequired: {
    ar: 'يجب إعداد التحقق بخطوتين قبل تنفيذ هذه العملية.',
    en: 'You need to set up two-step verification before you can do this.',
  },
  goEnrol: { ar: 'إعداد التحقق بخطوتين', en: 'Set up two-step verification' },
} as const
