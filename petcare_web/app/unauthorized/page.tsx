export default function UnauthorizedPage({
  searchParams,
}: {
  searchParams: { from?: string; required?: string }
}) {
  const from = searchParams.from ?? ''
  const required = searchParams.required?.split(',') ?? []

  const roleLabels: Record<string, string> = {
    owner: 'مالك حيوان أليف',
    vet: 'طبيب بيطري مرخّص',
    pharmacy: 'مشغّل صيدلية',
    admin: 'مدير المنصة',
  }

  return (
    <main style={{ maxWidth: 520, margin: '80px auto', padding: '0 24px' }}>
      <div className="card stack" style={{ textAlign: 'center', padding: 40 }}>
        <div>
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ margin: '0 auto' }} aria-label="وصول مقيّد">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
        </div>
        <div>
          <div className="title-lg">وصول مقيّد</div>
          <p className="subtitle">
            {from
              ? `الصفحة ${from} تتطلب دوراً محدداً للوصول.`
              : 'ليس لديك صلاحية لعرض هذه الصفحة.'}
          </p>
        </div>

        {required.length > 0 && (
          <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
            <span className="muted" style={{ alignSelf: 'center' }}>الدور المطلوب:</span>
            {required.map(r => (
              <span key={r} className="badge badge-blue">
                {roleLabels[r] ?? r}
              </span>
            ))}
          </div>
        )}

        <div className="divider" />

        <p className="muted">
          إذا كان لديك حساب، سجّل الدخول وسيتم تعيين دورك تلقائياً.
          يتوفر تسجيل العيادات والأطباء إذا كنت تنضم إلى برنامج التجريب.
        </p>

        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <a className="button" href="/signin">تسجيل الدخول</a>
          <a className="button button-outline" href="/">العودة للرئيسية</a>
        </div>
      </div>
    </main>
  )
}
