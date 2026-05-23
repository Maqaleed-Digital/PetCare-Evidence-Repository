'use client'

import { useLang } from '@/components/LangProvider'

export default function VetPage() {
  const { lang } = useLang()
  const isAr = lang === 'ar'

  return (
    <main className="stack">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div className="kicker">{isAr ? 'بوابة الطبيب البيطري' : 'Vet portal'}</div>
          <div className="title-lg">{isAr ? 'قائمة الاستشارات' : 'Consultation queue'}</div>
        </div>
        <span className="badge badge-green"><span className="icon-dot green" />{isAr ? 'التدقيق نشط' : 'Audit active'}</span>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="table">
          <thead>
            <tr>
              <th>{isAr ? 'الحالة' : 'Case'}</th>
              <th>{isAr ? 'المريض' : 'Patient'}</th>
              <th>{isAr ? 'الحالة' : 'Status'}</th>
              <th>{isAr ? 'الإجراء' : 'Action'}</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{isAr ? 'قائمة الاستشارات' : 'Consultation queue'}</td>
              <td>—</td>
              <td><span className="badge badge-amber">{isAr ? 'بانتظار' : 'Waiting'}</span></td>
              <td><a className="button button-outline button-sm" href="#">{isAr ? 'فتح' : 'Open'}</a></td>
            </tr>
            <tr>
              <td>{isAr ? 'الملاحظة السريرية (SOAP)' : 'Clinical note (SOAP)'}</td>
              <td>—</td>
              <td><span className="badge badge-gray">{isAr ? 'مسودة' : 'Draft'}</span></td>
              <td><a className="button button-outline button-sm" href="#">{isAr ? 'مراجعة وتوقيع' : 'Review & sign'}</a></td>
            </tr>
            <tr>
              <td>{isAr ? 'الوصفة الطبية' : 'Prescription'}</td>
              <td>—</td>
              <td><span className="badge badge-amber">{isAr ? 'معلّقة' : 'Pending'}</span></td>
              <td><a className="button button-outline button-sm" href="#">{isAr ? 'تفويض' : 'Authorize'}</a></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="note">
        <span className="muted">{isAr ? 'التوقيع السريري يتم من قبل الطبيب فقط وغير قابل للتعديل بعد الاكتمال. جميع تفويضات الوصفات متتبعة.' : 'Clinical sign-off is human-only and immutable once completed. All prescription authorizations are audit-traced.'}</span>
      </div>
    </main>
  )
}
