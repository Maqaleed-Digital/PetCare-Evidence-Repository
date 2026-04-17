export const dynamic = 'force-dynamic'

export default function HomePage() {
  return (
    <main className="stack">
      {/* Hero */}
      <div className="hero">
        <div className="hero-eyebrow">منصة الرعاية البيطرية المحكومة</div>
        <h1 className="hero-title">
          صحة حيوانك الأليف،<br />بعناية موثوقة ورقابة طبية كاملة
        </h1>
        <p className="hero-sub">
          VetiCare تربط الملّاك والأطباء والصيدليات تحت منصة موحّدة —
          كل إجراء موثّق، وكل وصفة قابلة للتتبع، وكل استشارة موقّعة.
        </p>
        <div className="hero-actions">
          <a className="button button-white" href="/signin">تسجيل الدخول</a>
          <a className="button button-ghost" href="/onboarding">تسجيل عيادة</a>
        </div>
      </div>

      {/* Role portals */}
      <div>
        <p className="kicker">البوابات</p>
        <div className="grid cols2" style={{ marginTop: 12 }}>
          <div className="role-card">
            <div className="role-card-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-label="بوابة المالك">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
              </svg>
            </div>
            <div>
              <div className="title" style={{ fontSize: 16 }}>بوابة المالك</div>
              <p className="subtitle">ملفات الحيوانات الأليفة، الجدول الصحي، حجز المواعيد، وإدارة الموافقات.</p>
            </div>
            <a className="button button-outline button-sm" href="/owner">فتح بوابة المالك</a>
          </div>
          <div className="role-card">
            <div className="role-card-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-label="بوابة الطبيب">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
              </svg>
            </div>
            <div>
              <div className="title" style={{ fontSize: 16 }}>بوابة الطبيب البيطري</div>
              <p className="subtitle">قائمة الاستشارات، توقيع الملاحظات السريرية، توثيق الحالات، والإحالات الطارئة.</p>
            </div>
            <a className="button button-outline button-sm" href="/vet">فتح بوابة الطبيب</a>
          </div>
          <div className="role-card">
            <div className="role-card-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-label="بوابة الصيدلية">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <line x1="12" y1="8" x2="12" y2="16"/>
                <line x1="8" y1="12" x2="16" y2="12"/>
              </svg>
            </div>
            <div>
              <div className="title" style={{ fontSize: 16 }}>بوابة الصيدلية</div>
              <p className="subtitle">قائمة الوصفات، سير عمل الصرف، السلامة الدوائية، وحالات السلسلة الباردة.</p>
            </div>
            <a className="button button-outline button-sm" href="/pharmacy">فتح بوابة الصيدلية</a>
          </div>
          <div className="role-card">
            <div className="role-card-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-label="بوابة الإدارة">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
            </div>
            <div>
              <div className="title" style={{ fontSize: 16 }}>بوابة الإدارة</div>
              <p className="subtitle">إدارة المستأجرين، الأدوار، تصدير الأدلة، وتتبع سجل المراجعة.</p>
            </div>
            <a className="button button-outline button-sm" href="/admin">فتح بوابة الإدارة</a>
          </div>
        </div>
      </div>

      {/* Governance strip */}
      <div className="card card-sm" style={{ display: 'flex', gap: 24, flexWrap: 'wrap', alignItems: 'center' }}>
        <span className="badge badge-green"><span className="icon-dot green" />جميع الأنظمة تعمل</span>
        <span className="muted">الحوكمة المغلقة فعّالة</span>
        <span className="muted">·</span>
        <span className="muted">سجل المراجعة نشط</span>
        <span className="muted">·</span>
        <span className="muted">مرحلة التجريب</span>
      </div>
    </main>
  )
}
