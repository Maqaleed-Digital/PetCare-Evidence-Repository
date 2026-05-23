'use client'

import { useLang } from '@/components/LangProvider'

export default function AdminPage() {
  const { lang } = useLang()
  const isAr = lang === 'ar'

  return (
    <main className="stack">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div className="kicker">{isAr ? 'إدارة المنصة' : 'Platform admin'}</div>
          <div className="title-lg">{isAr ? 'الحوكمة والعمليات' : 'Governance & operations'}</div>
        </div>
        <span className="badge badge-green"><span className="icon-dot green" />{isAr ? 'الدستور مختوم' : 'Constitution sealed'}</span>
      </div>

      <div className="grid cols2">
        <div className="role-card">
          <div className="role-card-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
            </svg>
          </div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>{isAr ? 'المستأجرون' : 'Tenants'}</div>
            <p className="subtitle">{isAr ? 'قائمة العيادات، الحالة، وتتبع مجموعة التجريب. كل مستأجر معزول ومراقَب.' : 'Clinic listing, status, and pilot cohort tracking. Each tenant is isolated and audited.'}</p>
          </div>
          <span className="muted">{isAr ? 'عيادة واحدة في التجريب' : '1 clinic in pilot'}</span>
        </div>
        <div className="role-card">
          <div className="role-card-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>{isAr ? 'المستخدمون والأدوار' : 'Users & roles'}</div>
            <p className="subtitle">{isAr ? 'إسناد الأدوار، مراقبة الحد الأدنى من الصلاحيات، ومراجعة الوصول.' : 'Role assignment, least-privilege monitoring, and access review.'}</p>
          </div>
          <a className="button button-outline button-sm" href="#">{isAr ? 'مراجعة الأدوار' : 'Review roles'}</a>
        </div>
        <div className="role-card">
          <div className="role-card-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
          </div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>{isAr ? 'سجل التدقيق' : 'Audit log'}</div>
            <p className="subtitle">{isAr ? 'رؤية كاملة للتتبع عبر جميع الأحداث السريرية والمالية والإدارية.' : 'Full trace visibility across all clinical, financial, and admin events.'}</p>
          </div>
          <a className="button button-outline button-sm" href="/api/audit-test">{isAr ? 'اختبار التدقيق' : 'Test probe'}</a>
        </div>
        <div className="role-card">
          <div className="role-card-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
            </svg>
          </div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>{isAr ? 'تصدير الأدلة' : 'Evidence export'}</div>
            <p className="subtitle">{isAr ? 'حزم تقارير محكومة لمجلس الإدارة والمستثمرين والجهات التنظيمية.' : 'Governed reporting packs for board, investor, and regulator readouts.'}</p>
          </div>
          <a className="button button-outline button-sm" href="#">{isAr ? 'تصدير الحزمة' : 'Export pack'}</a>
        </div>
      </div>

      <div className="card card-sm" style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
        <div><div className="muted">{isAr ? 'حالة المنصة' : 'Platform state'}</div><div style={{ fontWeight: 700, marginTop: 4 }}>CONTROLLED_PRODUCTION_ACTIVE</div></div>
        <div><div className="muted">{isAr ? 'سلسلة التدقيق' : 'Audit chain'}</div><div style={{ fontWeight: 700, marginTop: 4, color: 'var(--success)' }}>{isAr ? 'نشط' : 'Live'}</div></div>
        <div><div className="muted">{isAr ? 'إغلاق عند الفشل' : 'Fail-closed'}</div><div style={{ fontWeight: 700, marginTop: 4, color: 'var(--success)' }}>{isAr ? 'فعّال' : 'Active'}</div></div>
        <div><div className="muted">{isAr ? 'عيادات التجريب' : 'Pilot clinics'}</div><div style={{ fontWeight: 700, marginTop: 4 }}>1 / 2 max</div></div>
      </div>
    </main>
  )
}
