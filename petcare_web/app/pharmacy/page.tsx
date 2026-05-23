'use client'

import { useLang } from '@/components/LangProvider'

export default function PharmacyPage() {
  const { lang } = useLang()
  const isAr = lang === 'ar'

  return (
    <main className="stack">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div className="kicker">{isAr ? 'بوابة الصيدلية' : 'Pharmacy portal'}</div>
          <div className="title-lg">{isAr ? 'قائمة الوصفات' : 'Prescription queue'}</div>
        </div>
        <span className="badge badge-green"><span className="icon-dot green" />{isAr ? 'التدقيق نشط' : 'Audit active'}</span>
      </div>

      <div className="grid cols2">
        <div className="role-card">
          <div className="role-card-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
            </svg>
          </div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>{isAr ? 'الوصفات الموثّقة' : 'Validated prescriptions'}</div>
            <p className="subtitle">{isAr ? 'تظهر فقط الوصفات الموقّعة من الطبيب. العناصر غير الموقّعة لا يمكن صرفها.' : 'Only vet-signed prescriptions appear here. Unsigned items are not dispatchable.'}</p>
          </div>
          <span className="muted">{isAr ? 'القائمة فارغة' : 'Queue empty'}</span>
        </div>
        <div className="role-card">
          <div className="role-card-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>{isAr ? 'فحوصات السلامة' : 'Safety checks'}</div>
            <p className="subtitle">{isAr ? 'تحذيرات التعارض الدوائي، تنبيهات الجرعة، وعلامات الاستبدال قبل الصرف.' : 'Contraindication warnings, dosage alerts, and substitution flags shown before dispense.'}</p>
          </div>
          <span className="muted">{isAr ? 'لا توجد تنبيهات نشطة' : 'No active alerts'}</span>
        </div>
        <div className="role-card">
          <div className="role-card-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
          </div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>{isAr ? 'تتبع السلسلة الباردة' : 'Cold-chain tracking'}</div>
            <p className="subtitle">{isAr ? 'حالة التعامل مع المنتجات المنظّمة. يُحظر الصرف إذا انقطعت سلسلة الحفظ.' : 'Regulated product handling state. Dispense blocked if chain-of-custody is broken.'}</p>
          </div>
          <span className="muted">{isAr ? 'لا توجد عناصر سلسلة باردة' : 'No cold-chain items'}</span>
        </div>
        <div className="role-card">
          <div className="role-card-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
            </svg>
          </div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>{isAr ? 'سجل الصرف' : 'Dispense log'}</div>
            <p className="subtitle">{isAr ? 'كل عملية صرف مؤرّخة ومنسوبة ومسجّلة بشكل غير قابل للتعديل.' : 'Every dispense action is timestamped, attributed, and immutably recorded.'}</p>
          </div>
          <span className="muted">{isAr ? 'لا توجد عمليات صرف بعد' : 'No dispenses yet'}</span>
        </div>
      </div>

      <div className="note">
        <span className="muted">{isAr ? 'عمليات الصرف غير قابلة للإلغاء بعد التأكيد. جميع السجلات تحمل معرّف ارتباط للتدقيق.' : 'Dispense actions are irreversible once confirmed. All entries carry a correlation ID for audit tracing.'}</span>
      </div>
    </main>
  )
}
