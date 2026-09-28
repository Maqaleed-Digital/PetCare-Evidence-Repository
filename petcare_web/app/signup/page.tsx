'use client'

/**
 * /signup — owner self-registration (MVC-EPC-D-001 D2, J-O1). Sponsor ruling 1: built fully, behind the SERVER switch
 * PETCARE_OWNER_SELF_REGISTRATION (production default OFF). When the server reports it OFF this page offers no form —
 * only the invite path — and the API refuses self-registration regardless of what any client sends.
 */
import { EmptyState, LoadingState, Page, useCopy } from '@/components/ui'
import { SelfRegisterForm, useSelfRegistrationEnabled } from '@/components/auth/AccountFlows'

const T = {
  title: { ar: 'إنشاء حساب', en: 'Create an account' },
  kicker: { ar: 'للملّاك', en: 'For pet owners' },
  inviteOnly: { ar: 'التسجيل حالياً بدعوة فقط. إن كان لديك رمز دعوة فأكمل التسجيل من صفحة الدعوة.',
                en: 'Registration is currently by invitation only. If you have an invite code, register from the invite page.' },
  invite: { ar: 'التسجيل برمز دعوة', en: 'Register with an invite code' },
  haveAccount: { ar: 'لديك حساب؟ سجّل الدخول', en: 'Already have an account? Sign in' },
}

export default function SignupPage() {
  const { tr } = useCopy()
  const enabled = useSelfRegistrationEnabled()
  return (
    <Page kicker={T.kicker} title={T.title} testId="signup">
      {enabled === null && <LoadingState />}
      {enabled === true && <SelfRegisterForm />}
      {enabled === false && (
        <EmptyState message={T.inviteOnly} action={<a className="ds-btn" href="/register">{tr(T.invite)}</a>} />
      )}
      <a className="ds-link" href="/signin">{tr(T.haveAccount)}</a>
    </Page>
  )
}
