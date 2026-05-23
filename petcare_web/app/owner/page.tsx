'use client'

import { useLang } from '@/components/LangProvider'

export default function OwnerPage() {
  const { lang } = useLang()
  const isAr = lang === 'ar'

  return (
    <main className="stack">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div className="kicker">{isAr ? 'بوابة المالك' : 'Owner portal'}</div>
          <div className="title-lg">{isAr ? 'حيواناتي الأليفة' : 'My pets'}</div>
        </div>
        <span className="badge badge-green"><span className="icon-dot green" />{isAr ? 'التدقيق نشط' : 'Audit active'}</span>
      </div>

      <div className="grid cols2">
        <div className="role-card">
          <div className="role-card-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
            </svg>
          </div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>{isAr ? 'ملف الحيوان الأليف' : 'Pet profile'}</div>
            <p className="subtitle">{isAr ? 'الهوية، النوع، العمر، الحساسية، التطعيمات، وبيانات الشريحة.' : 'Identity, species, age, allergies, vaccinations, and microchip data.'}</p>
          </div>
          <span className="muted">{isAr ? 'لا توجد حيوانات مسجلة بعد' : 'No pets registered yet'}</span>
        </div>
        <div className="role-card">
          <div className="role-card-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
            </svg>
          </div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>{isAr ? 'الجدول الصحي' : 'Health timeline'}</div>
            <p className="subtitle">{isAr ? 'الزيارات، الوصفات، نتائج المختبر، والأحداث السريرية بالترتيب.' : 'Visits, prescriptions, lab results, and clinical events in order.'}</p>
          </div>
          <span className="muted">{isAr ? 'لا توجد سجلات بعد' : 'No records yet'}</span>
        </div>
        <div className="role-card">
          <div className="role-card-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>{isAr ? 'المواعيد' : 'Appointments'}</div>
            <p className="subtitle">{isAr ? 'حجز وإعادة جدولة وإلغاء مع تتبع تدقيق كامل لكل إجراء.' : 'Book, reschedule, and cancel with full audit trace on each action.'}</p>
          </div>
          <a className="button button-outline button-sm" href="#">{isAr ? 'حجز موعد' : 'Book appointment'}</a>
        </div>
        <div className="role-card">
          <div className="role-card-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
            </svg>
          </div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>{isAr ? 'الموافقة' : 'Consent'}</div>
            <p className="subtitle">{isAr ? 'منح وسحب موافقة العلاج. كل تغيير مسجل بشكل غير قابل للتعديل.' : 'Capture and revoke treatment consent. Every change is immutably logged.'}</p>
          </div>
          <span className="muted">{isAr ? 'لا توجد موافقات نشطة' : 'No active consents'}</span>
        </div>
      </div>

      <div className="note">
        <span className="muted">{isAr ? 'جميع الإجراءات في هذه البوابة محكومة ومتتبعة. تسجيل الخروج يُلغي جلستك النشطة.' : 'All actions in this portal are governed and audit-traced. Signing out revokes your active session.'}</span>
      </div>
    </main>
  )
}
